from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse

from .models import Address, Customer, Neighborhood, Order, OrderProduct, Product, PaymentMethod
from .forms import AddressForm, CustomerForm, OrderForm, OrderProductForm, ProductForm, DeliverForm

from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory

from django.conf import settings

import os
import xlwt
import datetime
from decimal import Decimal
from django.utils.dateparse import parse_date

from xlrd import open_workbook
from order.models import City, District

from dal import autocomplete


def delivery_page(request):
    context = dict()
    today = datetime.date.today()
    orders = Order.objects.filter(delivery_date=today)
    context['orders'] = orders

    return render(request, 'delivery_page.html', context)


def deliver_order(request, id):
    context = dict()
        
    order = get_object_or_404(Order, id=id)
    order_form = DeliverForm(instance=order)
        
    OrderInlineFormSet = inlineformset_factory(
        Order,
        Order.products.through,
        fields=['product', 'quantity'],
        can_delete=False
    )
    order_inline_formset = OrderInlineFormSet(instance=order)

    if request.method == "POST":
        order_form = DeliverForm(request.POST, instance=order)
        order_formset = OrderInlineFormSet(request.POST, instance=order)

        if order_form.is_valid() and order_formset.is_valid():
            order = order_form.save(commit=True)
            
            order_products = order_inline_formset.save(commit=False)
            total_amount = 0
            for product in order_products:
                product.order = order
                total_amount += product.quantity*product.product.price
                product.save()
            
            order.total_amount = total_amount
            order.delivery_status = True
            order.save()
            messages.success(request, 'Sipariş Teslim Edildi.')
            return redirect('delivery_page')

        context['order_form'] = order_form
        context['order_formset'] = order_inline_formset
        messages.warning(request, 'Eksik Bilgi Girdiniz.')
        return render(request, 'deliver_order.html', context)

    context['order_form'] = order_form
    context['order_formset'] = order_inline_formset
    return render(request, 'deliver_order.html', context)


class CustomerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Customer.objects.all().order_by('phone1')

        if self.q:
            qs = qs.filter(phone1__contains=self.q)

        return qs


def export_orders_xls(request, date):
    if parse_date(date) is None:
        numbers = date.split('-')
        date = datetime.date(int(numbers[2]), int(numbers[1]), int(numbers[0]))
    else:
        date = parse_date(date)
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="orders-{date}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Orders')
    row_num = 0
    
    font_style = xlwt.XFStyle()    
    font_style.font.bold = True

    columns = ['Adı', 'Soyadı', 'Telefon', 'Adres', 'Sipariş', 'Toplam Tutar', 'Ödeme Şekli', 'Notlar' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Order.objects.filter(delivery_date=date)
    for row in rows:
        row_num += 1
        col_num = 0 
        ws.write(row_num, col_num, row.customer.first_name, font_style)
        ws.write(row_num, col_num + 1, row.customer.last_name, font_style)
        ws.write(row_num, col_num + 2, row.customer.phone1, font_style)
        ws.write(row_num, col_num + 3, row.customer.address.get_full_address(), font_style)
        string = ""
        for order in row.orderproduct_set.all():
            string += (order.product.category.name) + '-' + (order.product.name) + "-" + str(Decimal(order.quantity)) + "\n"
            
        ws.write(row_num, col_num + 4, string, font_style)
        ws.write(row_num, col_num + 5, row.total_amount, font_style)
        if row.payment_method is None:
            data = "***"
        else:
            data=row.payment_method.name
        ws.write(row_num, col_num + 6, data, font_style)
        ws.write(row_num, col_num + 7, row.notes, font_style)
        
            
            
    wb.save(response)
    return response


def index(request):
    context = dict()
    return render(request, 'index.html', context)


def customer(request):
    context = dict()
    context['customers'] = Customer.objects.all()
    return render(request, 'customer.html', context)


def order(request):
    context = dict()

    products = Product.objects.all()

    product_numbers = []
    for product in products:
        total = 0
        for ordered_product in product.orderproduct_set.all():
            total += ordered_product.quantity
        product_numbers.append(product.name + " "+ str(Decimal(total)))

    context['product_numbers'] = product_numbers
    
    context['orders'] = Order.objects.all().order_by('-createt_at')
    return render(request, 'order.html', context)

    
def add_customer(request):
    context = dict()
    address_form = AddressForm(request.POST or None)
    customer_form = CustomerForm(request.POST or None)
    if request.method == "POST":
        if address_form.is_valid() and customer_form.is_valid():
            address = address_form.save()
            customer = customer_form.save(commit=False)
            customer.address = address
            customer.save()

            messages.success(request, 'Kullanıcı Başarıyla Eklendi')
            return redirect('customer')

        else:
            context['address_form'] = address_form
            context['customer_form'] = customer_form
            messages.warning(request, "Hatalı yada eksik bilgi girdiniz")
            return render(request, 'add_customer.html', context)
    
    context['address_form'] = address_form
    context['customer_form'] = customer_form
    return render(request, 'add_customer.html', context)


def add_order(request):
    context = dict()
    # context['orderform'] = OrderForm()
    # context['orderproductform'] = OrderProductForm()
    # order_formset = inlineformset_factory(Order, OrderProduct, form=OrderForm, extra=6)
    order_form = OrderForm()
    order_formset = inlineformset_factory(
        Order,
        Order.products.through,
        fields=['product', 'quantity'],
        extra=7,
        max_num=9,
        can_delete=False,
        min_num=1,
        validate_min=True
    )
    
    # order_formset = modelformset_factory(OrderProduct, form=OrderProductForm, extra=2, max_num=5)
    context['order_formset'] = order_formset
    context['order_form'] = order_form

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        order_formset = order_formset(request.POST)

        if order_form.is_valid() and order_formset.is_valid():
            order = order_form.save(commit=True)
            order_products = order_formset.save(commit=False)
            total_amount = 0
            for product in order_products:
                product.order = order
                total_amount += product.quantity*product.product.price
                product.save()
            
            order.total_amount = total_amount
            order.save()
            return redirect('order')
        
        context['order_formset'] = order_formset
        context['order_form'] = order_form

        messages.warning(request, 'Eksik Bilgi girdiniz')
        return render(request, 'add_order.html', context)

    return render(request, 'add_order.html', context)


def load_neighborhoodes(request):
    district_id = request.GET.get('district')
    
    neighborhoodes = Neighborhood.objects.filter(
        district_id=district_id).order_by('name')
    print(neighborhoodes)
    return render(request, 'neighborhood_dropdown_list_options.html', {'neighborhoodes': neighborhoodes})


def add_district_and_neighborhood(request):
    file_name = os.path.join(settings.BASE_DIR, "mahalle.xls")
     
    file = open_workbook(file_name)
    sheet = file.sheet_by_index(0)
    col_num=0
    for row_num in range(sheet.nrows):
        district_name = (sheet.cell(row_num, col_num).value.strip()).title()
        neighborhood = (sheet.cell(row_num, col_num + 1).value.strip()).title()
        city = City.objects.first()
        district, district_created = District.objects.get_or_create(city=city, name=district_name)

        Neighborhood.objects.create(district=district, name=neighborhood)
        print(district, neighborhood)
    return redirect('index')


def add_product(request):
    context = dict()
    product_form = ProductForm(request.POST or None)
    if request.method == "POST":
        if product_form.is_valid():
            product_form.save()
            messages.success(request, "Ürün Başarıyla Eklendi.")
            return redirect('products')

        context['product_form'] = product_form
        messages.warning(request, 'Eksik Bilgi Girdiniz.')
    
    context['product_form'] = product_form
    return render(request, 'add_product.html', context)


def products(request):
    context = dict()
    products = Product.objects.all()
    context['products'] = products

    return render(request, 'product.html', context)


def update_product(request, id):
    context = dict()
    product = get_object_or_404(Product, id=id)
    product_form = ProductForm(instance=product)

    if request.method == "POST":
        product = ProductForm(request.POST, instance=product)
        if product.is_valid():
            product.save()
            messages.success(request, 'Ürün Başarıyla Güncellendi.')
            return redirect('products')

        messages.warning(request, 'Eksik Bilgi Girdiniz.')

    context['product_form'] = product_form
    return render(request, 'add_product.html', context)


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, 'Ürün Silindi')
    return redirect('products')


def update_customer(request, id):
    context = dict()
    customer = get_object_or_404(Customer, id=id)
    address_form = AddressForm(instance=customer.address)
    customer_form = CustomerForm(instance=customer)

    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        address_form = AddressForm(request.POST, instance=customer.address)
        if customer_form.is_valid() and address_form.is_valid():
            customer_form.save()
            address_form.save()

            messages.success(request, 'Müşteri Bilgileri Başarıyla Güncellendi.')
            return redirect('customer')
        
        messages.warning(request, 'Eksik Bilgi Girdiniz.')

    context['address_form'] = address_form
    context['customer_form'] = customer_form
    return render(request, 'add_customer.html', context)


def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    messages.success(request, 'Müşteri Bilgileri Başarıyla Silindi.')
    return redirect('customer')


def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    messages.success(request, 'Sipariş Başarıyla Silindi.')
    return redirect('order')


def update_order(request, id):
    context = dict()
    order = get_object_or_404(Order, id=id)
    order_form = OrderForm(instance=order)
    
    OrderInlineFormSet = inlineformset_factory(
        Order,
        Order.products.through,
        fields=['product', 'quantity'],
        extra=7,
        max_num=9,
        can_delete=False
    )
    order_inline_formset = OrderInlineFormSet(instance=order)

    if request.method == "POST":
        order_form = OrderForm(request.POST, instance=order)
        order_inline_formset = OrderInlineFormSet(request.POST, instance=order)

        if order_form.is_valid() and order_inline_formset.is_valid():
            order = order_form.save(commit=True)
            
            order_products = order_inline_formset.save(commit=False)
            total_amount = 0
            for product in order_products:
                product.order = order
                total_amount += product.quantity*product.product.price
                product.save()
            
            order.total_amount = total_amount
            order.save()
            messages.success(request, 'Sipariş Bilgileri Başarıyla Güncellendi.')
            return redirect('order')
        
        context['order_form'] = order_form
        context['order_formset'] = order_inline_formset
        messages.warning(request, 'Eksik Bilgi Girdiniz.')
        return render(request, 'add_order.html', context)

    context['order_form'] = order_form
    context['order_formset'] = order_inline_formset
    
    return render(request, 'add_order.html', context)


def daily_order(request, date):
    context = dict()    
    if parse_date(date) is None:
        numbers = date.split('-')
        date = datetime.date(int(numbers[2]), int(numbers[1]), int(numbers[0]))
    else:
        date = parse_date(date)

    days = []
    today = datetime.date.today()
    for i in range(0, 7):
        days.append(today + datetime.timedelta(i))

    context['days'] = days

    """"orders"""
    products = Product.objects.all()

    product_numbers = []
    for product in products:
        total = 0
        for ordered_product in product.orderproduct_set.filter(order__delivery_date=date):
            total += ordered_product.quantity
        product_numbers.append(product.name + " "+ str(Decimal(total)))

    context['product_numbers'] = product_numbers
    orders = Order.objects.filter(delivery_date=date).order_by('-createt_at')
    context['orders'] = orders
    context['exact_date'] = date
    return render(request, 'daily_order.html', context)


def search_status(request):

    if request.method == "GET":
        search_text = request.GET['search_text']
        if search_text is not None and search_text != u"":
            search_text = request.GET['search_text']
            print(search_text)
            phones = Customer.objects.filter(phone1__contains = search_text)
            print(phones)
        else:
            phones = []

        return render(request, 'ajax_search.html', {'phones':phones})
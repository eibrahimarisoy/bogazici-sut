from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse

from .models import Address, Customer, Neighborhood, Order, OrderItem, Product, PaymentMethod
from .forms import AddressForm, CustomerForm, OrderForm, OrderItemForm, ProductForm, DeliverForm, BaseModelFormSet

from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory, formset_factory

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
        
    OrderItemFormSet = modelformset_factory(
        OrderItem,
        form=OrderItemForm,
        # max_num=9,
        min_num=1,
        extra=5,
        can_delete=True,
        )

    order_item_form_set = OrderItemFormSet(queryset=order.items.all())

    if request.method == "POST":
            order_form = DeliverForm(request.POST, instance=order)
            order_item_form_set = OrderItemFormSet(request.POST)

            if order_form.is_valid() and order_item_form_set.is_valid():
                order = order_form.save(commit=True)
                order_items = order_item_form_set.save(commit=False)
                for obj in order_item_form_set.deleted_objects:
                    obj.delete()

                for item in order_items:
                    item.save()
                    order.items.add(item)

                order.total_price_update()
                order.is_delivered = True
                order.save()
                messages.success(request, 'Sipariş Bilgileri Başarıyla Güncellendi.')
                return redirect('delivery_page')

            context['order'] = order
            context['order_form'] = order_form
            context['order_formset'] = order_item_form_set
            messages.warning(request, 'Eksik Bilgi Girdiniz.')
            return render(request, 'deliver_order.html', context)

    context['order'] = order
    context['order_form'] = order_form
    context['order_formset'] = order_item_form_set
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

    columns = ['Telefon',' Adres', 'Tavuk', 'Yumurta', 'Süt', 'Tereyağ', 'Peynir', 'Toplam Tutar', 'Ödeme Şekli', 'Notlar' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Order.objects.filter(delivery_date=date)
    for row in rows:
        row_num += 1
        col_num = 0 
        ws.write(row_num, col_num, row.customer.phone1, font_style)
        ws.write(row_num, col_num + 1, row.customer.address.get_full_address(), font_style)

        tavuk, yumurta, süt, tereyağ, peynir = "", "", "", "", ""
        
        notes = row.notes
        
        for order in row.orderitem_set.all():
            if order.product.category.name == "Tavuk":
                tavuk += (order.product.name + "\n") * int(order.quantity)
            
            elif order.product.category.name == "Yumurta":
                yumurta += (order.product.name + "\n") * int(order.quantity)
            
            elif order.product.category.name == "Süt":
                süt += (order.product.name + "\n") * int(order.quantity)

            elif order.product.category.name == "Tereyağ":
                tereyağ += str(Decimal(order.quantity))

            elif order.product.category.name == "Peynir":
                peynir += (order.product.name + "\n") * int(order.quantity)
            
        if row.is_instagram:
            notes += "\nKullanıcı Adı:" + row.instagram_username

        ws.write(row_num, col_num + 2, tavuk, font_style)
        ws.write(row_num, col_num + 3, yumurta, font_style)
        ws.write(row_num, col_num + 4, süt, font_style)
        ws.write(row_num, col_num + 5, tereyağ, font_style)
        ws.write(row_num, col_num + 6, peynir, font_style)
        ws.write(row_num, col_num + 7, row.total_amount, font_style)
        ws.write(row_num, col_num + 8, "", font_style)
        ws.write(row_num, col_num + 9, notes, font_style)
        
            
            
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

    """"orders"""
    products = Product.objects.all()

    number_of_order_items = []


    for product in products:
        total = 0
        for item in product.orderitem_set.all():
            total += item.quantity

        number_of_order_items.append(f"{str(Decimal(total))} x {product.name}")

    context['product_numbers'] = number_of_order_items
    
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
    order_form = OrderForm()

    OrderItemFormSet = modelformset_factory(
        OrderItem,
        form=OrderItemForm,
        formset=BaseModelFormSet,
        max_num=8,
        extra=5,
        min_num=1,
        )
    context['order_formset'] = OrderItemFormSet()
    context['order_form'] = order_form

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        order_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and order_formset.is_valid():
            order = order_form.save(commit=True)
            order_products = order_formset.save(commit=False)
            for item in order_products:
                item.save()
                order.items.add(item)

            order.total_price_update()
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

    # TODO formset max and maybe another template
    OrderItemFormSet = modelformset_factory(
        OrderItem,
        form=OrderItemForm,
        # max_num=9,
        min_num=1,
        extra=5,
        can_delete=True,
        )

    order_item_form_set = OrderItemFormSet(queryset=order.items.all())

    if request.method == "POST":
        order_form = OrderForm(request.POST, instance=order)
        order_item_form_set = OrderItemFormSet(request.POST)

        if order_form.is_valid() and order_item_form_set.is_valid():
            order = order_form.save(commit=True)
            order_items = order_item_form_set.save(commit=False)
            for obj in order_item_form_set.deleted_objects:
                obj.delete()
            
            for item in order_items:
                item.save()
                order.items.add(item)

            order.total_price_update()
            order.save()
            messages.success(request, 'Sipariş Bilgileri Başarıyla Güncellendi.')
            return redirect('order')
        
        context['order_form'] = order_form
        context['order_formset'] = order_item_form_set
        messages.warning(request, 'Eksik Bilgi Girdiniz.')
        return render(request, 'add_order.html', context)

    context['order_form'] = order_form
    context['order_formset'] = order_item_form_set
    
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

    number_of_order_items = []


    for product in products:
        total = 0
        for item in product.orderitem_set.all().filter(order_item__delivery_date=date):
            total += item.quantity

        number_of_order_items.append(f"{str(Decimal(total))} x {product.name}")

    context['product_numbers'] = number_of_order_items
    orders = Order.objects.filter(delivery_date=date).order_by('-createt_at')
    context['orders'] = orders
    context['exact_date'] = date

    """payments"""
    pay_at_door = 0
    eft = 0

    for order in orders:
        
        if order.payment_method_id == 2:
            pay_at_door += order.received_money
        elif order.payment_method_id == 1: 
            eft += order.total_price
    
    context['pay_at_door'] = pay_at_door
    context['eft'] = eft
            
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
# -*- coding: utf-8 -*-

import datetime
import os
from datetime import timedelta
from decimal import Decimal
from string import capwords

import vobject
import xlwt
from dal import autocomplete
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.db.models.functions import Length
from django.forms import formset_factory, modelformset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from xlrd import open_workbook

from order.models import Category, City, District
from user.forms import LoginForm

from .forms import (AddressForm, BaseModelFormSet, CustomerForm,
                    CustomerSearchForm, DeliverForm, OrderCalendarForm,
                    OrderForm, OrderItemForm, ProductForm)
from .models import Address, Customer, Neighborhood, Order, OrderItem, Product


@login_required
def delivery_page(request):
    context = dict()
    today = datetime.date.today()
    orders = Order.objects.filter(delivery_date=today).order_by('customer__address__district__name')
    context['orders'] = orders

    return render(request, 'delivery_page.html', context)


@login_required
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
                if order.payment_method == 1:  # check payment method for cash
                    order.is_paid = True
                elif order.payment_method == 2:
                    order.is_paid = False
                    order.remaining_debt = order.total_price - order.received_money
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
        qs = Customer.objects.all().order_by('phone1')
        if self.q:
            qs = qs.filter(Q(phone1__contains=self.q) | Q(first_name__icontains=self.q))
            # qs1 = qs.filter(first_name__icontains=self.q)
        return qs


@staff_member_required
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

    columns = ['Sıra No', 'Sipariş Kodu', 'Ad Soyad', 'Telefon', ' Adres', 'Tavuk', 'Yumurta', \
               'Süt', 'Tereyağ', 'Peynir', 'Sucuk', 'Toplam Tutar', 'Ödeme Şekli', \
               'Notlar' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    orders = Order.objects.filter(delivery_date=date).order_by('customer__address__district__name')

    categories = Category.objects.all()
    products = Product.objects.all()
    
    i = 0
    for category in categories:
        number_of_order_items = []
        col_num = 5
        for product in products.filter(category=category):
            total = 0
            for item in product.orderitem_set.all().filter(order_item__delivery_date=date):
                total += item.quantity

            number_of_order_items.append(f"{str(Decimal(total))} x {product.name} \n")
        ws.write(row_num + 2, col_num + i, number_of_order_items, font_style)
        i += 1
    
    total_amount = 0
    for order in orders:
        total_amount += order.total_price
        
    ws.write(row_num +2, 11, total_amount, font_style)

    row_num = 3
    col_num = 0
    for order in orders:
        row_num += 1
        col_num = 0
        ws.write(row_num, col_num, f"{row_num-3}", font_style)
        ws.write(row_num, col_num + 1, order.nick, font_style)
        ws.write(row_num, col_num + 2, f"{order.customer.first_name.upper()} {order.customer.last_name.upper()}", font_style)
        ws.write(row_num, col_num + 3, order.customer.phone1, font_style)
        ws.write(row_num, col_num + 4, order.customer.address.get_full_address().upper(), font_style)

        tavuk, yumurta, süt, tereyağ, peynir, sucuk = "", "", "", "", "", ""
               
        for item in order.items.all():
            if item.product.category.name == "Tavuk":
                tavuk += (item.product.name + "\n") * int(item.quantity)
            
            elif item.product.category.name == "Yumurta":
                yumurta += str(Decimal(item.quantity))
            
            elif item.product.category.name == "Süt":
                süt += (item.product.name + "\n") * int(item.quantity)

            elif item.product.category.name == "Tereyağ":
                tereyağ += (item.product.name) + " " + str(Decimal(item.quantity))

            elif item.product.category.name == "Peynir":
                peynir += (item.product.name + "\n") * int(item.quantity)

            elif item.product.category.name == "Sucuk":
                sucuk += f"{Decimal(item.quantity)} {item.product.distribution_unit}"

        notes = order.notes
        if order.is_instagram:
            notes += "\nKullanıcı Adı:" + order.instagram_username

        if len(order.customer.order_set.all()) == 1:
            notes = "***İlk Sipariş***"

        ws.write(row_num, col_num + 5, tavuk.upper(), font_style)
        ws.write(row_num, col_num + 6, yumurta.upper(), font_style)
        ws.write(row_num, col_num + 7, süt.upper(), font_style)
        ws.write(row_num, col_num + 8, tereyağ.upper(), font_style)
        ws.write(row_num, col_num + 9, peynir.upper(), font_style)
        ws.write(row_num, col_num + 10, sucuk.upper(), font_style)
        ws.write(row_num, col_num + 11, order.total_price, font_style)
        ws.write(row_num, col_num + 12, "", font_style)
        ws.write(row_num, col_num + 13, notes.upper(), font_style)
                    
    wb.save(response)
    return response


def index(request):
    context = dict()
    login_form = LoginForm(request.POST or None)
    context['login_form'] = login_form

    if login_form.is_valid():
        email = login_form.cleaned_data.get("email")
        password = login_form.cleaned_data.get("password")

        # if username is not exists throw and error to user
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.info(request, "Kullanıcı Adı Yanlış.")
            return render(request, "index.html", context)

        # check username and password are correct
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.info(request, "Kullanıcı Adı veya Parolanız Yanlış")
            return render(request, "index.html", context)
        else:
            messages.success(request, "Başarıyla Giriş Yaptınız")
            # start new session for user
            login(request, user)
            return redirect("index")

    return render(request, 'index.html', context)


@staff_member_required
def customer(request):
    context = dict()
    customers = Customer.objects.all().order_by('-pk')
    customer_search_form = CustomerSearchForm()
    page = request.GET.get('page', 1)
    paginator = Paginator(customers, 30)

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    context['customers'] = customers
    context['customer_search_form'] = customer_search_form

    return render(request, 'customer.html', context)


@staff_member_required
def order(request):
    context = dict()

    """"orders"""
    products = Product.objects.all().order_by('-createt_at')

    number_of_order_items = []


    for product in products:
        total = 0
        for item in product.orderitem_set.all():
            total += item.quantity

        number_of_order_items.append(f"{str(Decimal(total))} x {product.name}")

    context['product_numbers'] = number_of_order_items
    
    context['orders'] = Order.objects.all().order_by('-createt_at')
    return render(request, 'order.html', context)


@staff_member_required
def add_customer(request):
    context = dict()
    address_form = AddressForm(request.POST or None)
    customer_form = CustomerForm(request.POST or None)
    if request.method == "POST":
        if address_form.is_valid() and customer_form.is_valid():
            customer = customer_form.save(commit=False)
            address = address_form.save()
            customer.address = address
            customer.nick = f"{customer.address.district.nick}-{len(Customer.objects.filter(address__district=customer.address.district))+1:04}"
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


@staff_member_required
def add_order(request, id=None):
    context = dict()
    order_form = OrderForm()
    if id is not None:
        order_form = OrderForm(initial={'customer' :Customer.objects.get(id=id)})
    
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
            messages.success(request, 'Sipariş Başarıyla Kaydedildi.')
            return redirect('order')
        
        context['order_formset'] = order_formset
        context['order_form'] = order_form

        messages.warning(request, 'Eksik Bilgi girdiniz')
        return render(request, 'add_order.html', context)

    return render(request, 'add_order.html', context)


@staff_member_required
def load_neighborhoodes(request):
    district_id = request.GET.get('district')
    
    neighborhoodes = Neighborhood.objects.filter(
        district_id=district_id).order_by('name')
    return render(request, 'neighborhood_dropdown_list_options.html', {'neighborhoodes': neighborhoodes})


@staff_member_required
def ajax_customer_search(request):
    phone1 = request.GET.get('phone_number')

    customer = get_object_or_404(Customer, phone1=phone1)
    return render(request, 'customer_result_table.html', {'customer': customer})


@staff_member_required
def add_district_and_neighborhood(request):
    file_name = os.path.join(settings.BASE_DIR, "mahalle1.xls")
     
    file = open_workbook(file_name)
    sheet = file.sheet_by_index(0)
    col_num=0
    for row_num in range(sheet.nrows):
        district_name = (sheet.cell(row_num, col_num).value.strip())
        neighborhood = (sheet.cell(row_num, col_num + 1).value.strip())

        city = City.objects.first()
        district, district_created = District.objects.get_or_create(city=city, name=district_name)

        Neighborhood.objects.create(district=district, name=neighborhood)
        print(district_name, neighborhood)
    return redirect('index')


@staff_member_required
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


@staff_member_required
def products(request):
    context = dict()
    products = Product.objects.all()
    context['products'] = products

    return render(request, 'product.html', context)


@staff_member_required
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


@staff_member_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, 'Ürün Silindi')
    return redirect('products')


@staff_member_required
def update_customer(request, id):
    context = dict()
    customer = get_object_or_404(Customer, id=id)
    address_form = AddressForm(instance=customer.address)
    customer_form = CustomerForm(instance=customer)

    if request.method == "POST":
        customer_form = CustomerForm(request.POST or None, instance=customer)
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


@staff_member_required
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    messages.success(request, 'Müşteri Bilgileri Başarıyla Silindi.')
    return redirect('customer')


@staff_member_required
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    messages.success(request, 'Sipariş Başarıyla Silindi.')
    return redirect('order')


@staff_member_required
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
        order_item_form_set = OrderItemFormSet(request.POST, request.FILES)

        if order_form.is_valid() and order_item_form_set.is_valid():
            order = order_form.save(commit=True)
            order_items = order_item_form_set.save(commit=False)
            for obj in order_item_form_set.deleted_objects:
                obj.delete()
            for item in order_items:
                item.price = item.product.price
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


@staff_member_required
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
    orders = Order.objects.filter(delivery_date=date).order_by('customer__address__district__name')
    context['orders'] = orders
    context['exact_date'] = date

    """payments"""
    cash = 0
    eft = 0

    for order in orders:
        
        if order.payment_method == 1: # cash
            cash += order.received_money
        elif order.payment_method == 2: # eft
            eft += order.total_price
    
    context['cash'] = cash
    context['eft'] = eft
            
    return render(request, 'daily_order.html', context)


@staff_member_required
def add_customer_from_file(request):   
    file_name = os.path.join(settings.BASE_DIR, "../contacts_test.xls")
    file = open_workbook(file_name)
    sheet = file.sheet_by_index(0)
    
    col_num = 0
    for row_num in range(1, sheet.nrows):
        address = (sheet.cell(row_num, col_num).value.strip())
        phone = (sheet.cell(row_num, col_num + 1).value.strip())

        address_list = address.split()
        district = address_list[0]
        neighborhood = address_list[1]
        print(address)

        try:
            district_name = District.objects.get(name__icontains=district)
        except District.DoesNotExist:
            continue

        try:
            neighborhood_name = Neighborhood.objects.get(name__contains=neighborhood, district=district_name)
        except Neighborhood.DoesNotExist:
            continue

        address_info = ""
        for item in range(2, len(address_list)):
            address_info += address_list[item] + " "

        city = City.objects.first()
        address = Address.objects.create(city=city, district=district_name, neighborhood=neighborhood_name, address_info=address_info) 

        customer, created = Customer.objects.get_or_create(phone1=phone, address=address)

    return redirect('index')


@staff_member_required
def download_customer_vcf(request, id):
    customer = get_object_or_404(Customer, id=id)
    v = vobject.vCard()
    v.add('fn')
    v.fn.value = f"{customer.address.get_full_address()}"
    v.add('tel')
    v.tel.value = f"{customer.phone1}"
    v.tel.type_param = 'WORK'
              
    response = HttpResponse(content_type="text/vCard")
    response['Content-Disposition'] = f"attachment; filename={customer.phone1}.vcf"
    response.write(v.serialize())
    return response


@staff_member_required
def number_of_customer_orders(request):
    context = dict()
    customers = Customer.objects.exclude(order=None).annotate(num_orders=Count('order')) \
                .order_by('num_orders')

    context['customers'] = customers
    return render(request, 'number_of_customer_orders.html', context)

@staff_member_required
def payment_method_set(request, id, method):
    order = get_object_or_404(Order, id=id)
    
    try:
        if method == "Nakit":
            order.payment_method = 1
            order.received_money = order.total_price
            order.is_delivered = True
            order.remaining_debt = 0
            order.is_paid = True
        if method == "EFT":
            order.payment_method = 2
            order.remaining_debt = order.total_price
            order.is_delivered = True
            order.is_paid = False

        order.save()
    except:
        pass
    return redirect('delivery_page')


@staff_member_required
def unpaid_orders(request):
    context = dict()
    unpaid_orders = Order.objects.filter(
        is_paid=False,
        is_delivered=True,
    )
    context['unpaid_orders'] = unpaid_orders
    return render(request, 'unpaid_orders.html', context)


@staff_member_required
def pay_with_eft(request, id):
    order = get_object_or_404(Order, id=id, payment_method=2)
    order.received_money = order.remaining_debt + order.received_money
    order.remaining_debt = 0
    order.is_paid = True
    order.save()
    return redirect('unpaid_orders')


@staff_member_required
def order_calendar(request):
    context = dict()
    order_calendar_form = OrderCalendarForm(request.GET or None)
    date = datetime.date.today()
    
    if order_calendar_form.is_valid():
        date = order_calendar_form.cleaned_data.get('date')
           
    orders = Order.objects.filter(delivery_date=date)

    """"orders"""
    products = Product.objects.all()
    number_of_order_items = []

    for product in products:
        total = 0
        for item in product.orderitem_set.all().filter(order_item__delivery_date=date):
            total += item.quantity

        number_of_order_items.append(f"{str(Decimal(total))} x {product.name}")

    context['product_numbers'] = number_of_order_items

    context['orders'] = orders
    context['order_calendar_form'] = order_calendar_form
    return render(request, 'order_calendar.html', context)


@staff_member_required
def daily_revenue(request):
    context = dict()
    order_calendar_form = OrderCalendarForm(request.GET or None)
    date = datetime.date.today()
    
    if order_calendar_form.is_valid():
        date = order_calendar_form.cleaned_data.get('date')

    daily_orders = Order.objects.filter(delivery_date=date)
    
    received_money = 0
    not_received_money = 0
    
    for item in daily_orders:
        received_money += item.received_money
        not_received_money += item.remaining_debt
        

    # getting unpaid orders
    unpaid_orders = daily_orders

    context['unpaid_orders'] = unpaid_orders
    context['received_money'] = received_money
    context['not_received_money'] = not_received_money
    context['order_calendar_form'] = order_calendar_form
    return render(request, 'daily_revenue.html', context)


def order_report(request):
    context = dict()
    order_calendar_form = OrderCalendarForm(request.GET or None)
    date = datetime.date.today()

    if order_calendar_form.is_valid():
        date = order_calendar_form.cleaned_data.get('date')
           
    day = date.weekday()
    delta_to_start = timedelta(days=day)
    delta_to_end = timedelta(days=6 - day)

    orders = Order.objects.filter(delivery_date__gte=(date - delta_to_start)). \
        filter(delivery_date__lte=date + delta_to_end)
    
    """"orders"""
    products = Product.objects.all()
    number_of_order_items = []

    districts = District.objects.all()
    
    for product in products:
        item_list = [product.name]
        for district in districts:
            total = 0            
            for item in product.orderitem_set. \
                filter(order_item__customer__address__district=district). \
                filter(order_item__delivery_date__gte=(date - delta_to_start)). \
                filter(order_item__delivery_date__lte=date + delta_to_end):
                total += item.quantity

            item_list.append((Decimal(total)))
        sub_total = 0
        for i in range(1, len(item_list)):
            sub_total += item_list[i]
        item_list.append(sub_total)
        number_of_order_items.append(item_list)

    context['districts'] = districts
    context['week_start'] = date - delta_to_start
    context['week_end'] = date + delta_to_end
    context['products'] = number_of_order_items
    context['order_calendar_form'] = order_calendar_form
    return render(request, 'order_report.html', context)


def customer_details(request, id):
    context = dict()
    customer = get_object_or_404(Customer, id=id)
    context['customer'] = customer
    return render(request, 'customer_details.html', context)
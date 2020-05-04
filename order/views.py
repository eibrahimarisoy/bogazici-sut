from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse

from .models import Address, Customer, Neighborhood, Order, OrderProduct, Product
from .forms import AddressForm, CustomerForm, OrderForm, OrderProductForm

from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory

import xlwt
import datetime

# Create your views here.

def export_orders_xls(request):
    time=datetime.date.today()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="orders-{time}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Orders')
    row_num = 0
    
    font_style = xlwt.XFStyle()    
    font_style.font.bold = True

    columns = ['Adı', 'Soyadı', 'Telefon', 'Adres', 'Sipariş', 'Toplam Tutar', 'Ödeme Şekli', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Order.objects.all()
    for row in rows:
        row_num += 1
        col_num = 0 
        ws.write(row_num, col_num, row.customer.first_name, font_style)
        ws.write(row_num, col_num + 1, row.customer.last_name, font_style)
        ws.write(row_num, col_num + 2, row.customer.phone1, font_style)
        ws.write(row_num, col_num + 3, row.customer.address.get_full_address(), font_style)
        string = ""
        for order in row.orderproduct_set.all():
            string += (order.product.category.name) + '-' + (order.product.name) + "-" + str(order.quantity) + "-" + str(order.get_distribution_unit_display()) + "\n"
            
        ws.write(row_num, col_num + 4, string, font_style)
        ws.write(row_num, col_num + 5, row.total_amount, font_style)
        if row.payment_method is None:
            data = "***"
        else:
            data=row.payment_method.name
        ws.write(row_num, col_num + 6, data, font_style)
        
            
            



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
        product_numbers.append(product.name + " "+ str(total))

    context['product_numbers'] = product_numbers
    
    context['orders'] = Order.objects.all()
    return render(request, 'order.html', context)

    
def add_customer(request):
    context = dict()
    if request.method == "POST":
        address_form = AddressForm(request.POST)
        customer_form = CustomerForm(request.POST)

        if address_form.is_valid() and customer_form.is_valid():
            address = address_form.save()
            customer = customer_form.save(commit=False)
            customer.address = address
            customer.save()

            messages.success(request, 'Kullanıcı Başarıyla Eklendi')
            return redirect('customer')

        else:
            context['addressform'] = address_form
            context['customerform'] = customer_form
            messages.warning(request, "Hatalı yada eksik bilgi girdiniz")
            return render(request, 'add_customer.html', context)
    
    context['addressform'] = AddressForm()
    context['customerform'] = CustomerForm()
    return render(request, 'add_customer.html', context)


def add_order(request):
    context = dict()
    # context['orderform'] = OrderForm()
    # context['orderproductform'] = OrderProductForm()
    # order_formset = inlineformset_factory(Order, OrderProduct, form=OrderForm, extra=6)
    order_form = OrderForm()
    order_formset = inlineformset_factory(Order, Order.products.through, fields=['product', 'quantity'], extra=3, max_num=9)
    
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

# def load_townships(request):
#     district_id = request.GET.get('district')
#     townships = Township.objects.filter(
#         district_id=district_id).order_by('name')
#     print(townships)
#     return render(request, 'advertisement/township_dropdown_list_options.html', {'townships': townships})

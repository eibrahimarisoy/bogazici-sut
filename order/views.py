from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count

from .models import Address, Customer, Neighborhood, Order, OrderProduct, Product
from .forms import AddressForm, CustomerForm, OrderForm, OrderProductForm

from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory

# Create your views here.

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
    order_formset = inlineformset_factory(Order, Order.products.through, fields=['product', 'quantity'], extra=6)
    
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

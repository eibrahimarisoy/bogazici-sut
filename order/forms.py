from django import forms
from django.forms import BaseModelFormSet
from .models import Address, Customer, OrderItem, Order, Product
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Reset, Row, Submit
import datetime
from tempus_dominus.widgets import DatePicker

from dal import autocomplete
from django.forms.widgets import SelectDateWidget
from django.contrib.admin import widgets


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'name', 'distribution_unit', 'price')
        

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('district', 'neighborhood', 'address_info',)

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'phone1', 'phone2')


class DeliverForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['notes', 'delivery_date', 'payment_method', 'received_money']
    
    def __init__(self, *args, **kwargs):
        super(DeliverForm, self).__init__(*args, **kwargs)

        self.fields['delivery_date'].required = True
        self.fields['payment_method'].required = True
        self.fields['received_money'].required = True
        self.fields['notes'].required = False
        self.fields['received_money'].label = "Tahsilat"


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['customer', 'delivery_date', 'notes', 'is_instagram', 'instagram_username']

    customer = forms.ModelChoiceField(
        label="Müşteri",
        queryset=Customer.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='customer_autocomplete',
            attrs={
                # Set some placeholder
                'data-placeholder': 'Müşteri Telefon No...',
                },
    ))

    instagram_username= forms.CharField(label='', help_text="Kullanıcı Adı")
    delivery_date = forms.DateField(widget=AdminDateWidget(), initial=datetime.date.today())

    notes = forms.CharField(label="Notlar")
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields['customer'].required = True
        self.fields['delivery_date'].required = True
        self.fields['instagram_username'].required = False
        self.fields['notes'].required = False
        

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)

        self.fields['product'].required = True
        self.fields['quantity'].required = True


class BaseModelFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        # self.instance = kwargs.pop('instance')

        super().__init__(*args, **kwargs)
        self.queryset = Product.objects.none()
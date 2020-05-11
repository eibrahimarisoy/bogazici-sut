from django import forms
from .models import Address, Customer, OrderProduct, Order, Product
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Reset, Row, Submit
import datetime
from tempus_dominus.widgets import DatePicker

from dal import autocomplete


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
    
    
class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['customer', 'delivery_date', 'payment_method', 'notes', 'is_instagram', 'instagram_username']

    customer = forms.ModelChoiceField(
        label="Müşteri",
        queryset=Customer.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='customer_autocomplete',
            attrs={
                # Set some placeholder
                'data-placeholder': 'Müşteri Telefon No...',
                # Only trigger autocompletion after 3 characters have been typed
                'class': 'col',
                'style': {'height':'38px'},
                # 'data-minimum-input-length': 3,
                },
    ))

    instagram_username= forms.CharField(label='', help_text="Kullanıcı Adı")
    delivery_date = forms.DateField(
        label="Teslim Tarihi",
        widget=DatePicker(options={
            'minDate': '2020-01-01',
            'maxDate': '2022-01-01',
            'format': 'DD/MM/YYYY',
            'locale': "tr",
            'localize': True
        }),
        initial=datetime.date.today()
    )

    notes = forms.CharField(label="Notlar")
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields['customer'].required = True
        self.fields['delivery_date'].required = True
        self.fields['payment_method'].required = True
        self.fields['instagram_username'].required = False
        self.fields['notes'].required = False
        

class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super(OrderProductForm, self).__init__(*args, **kwargs)

        self.fields['product'].required = True
        self.fields['quantity'].required = True

from django import forms
from .models import Address, Customer, OrderProduct, Order
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, HTML, Layout, Reset, Row, Submit
import datetime

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
        
    instagram_username= forms.CharField(label='', help_text="Kullanıcı Adı")
    delivery_date = forms.DateField(label="Teslim Tarihi", widget=forms.SelectDateWidget,initial=datetime.date.today)
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
        fields = '__all__'
        exclude = ['order', 'distribution_unit',]

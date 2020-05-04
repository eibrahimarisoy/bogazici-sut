from django import forms
from .models import Address, Customer, OrderProduct, Order

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
        fields = '__all__'
        exclude = ['products', 'total_amount',]

class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = '__all__'
        exclude = ['order', 'distribution_unit',]

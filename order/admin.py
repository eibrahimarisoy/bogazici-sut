from django.contrib import admin
from .models import City, Neighborhood, District, Address, \
    Customer, Category, Product, Order, OrderItem
    


class DistrictAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'city',
        'nick'

    )
    list_editable = ('nick',)


class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'district'

    )
    list_editable = [
        'name'
    ]
    list_filter = ('district',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'nick',
        'first_name',
        'last_name',
        'phone1',
        'phone2',
        'address'
    )
    list_editable = ['nick']
    list_filter = ('address__district',)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'customer',
        'nick',
        'delivery_date',
        
    )
    list_editable = ['nick']
    list_filter = ('delivery_date',)
    

admin.site.register(City)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Address)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)

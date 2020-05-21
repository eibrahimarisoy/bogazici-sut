from django.contrib import admin
from .models import City, Neighborhood, District, Address, \
    Customer, Category, Product, Order, PaymentMethod, OrderItem
    


class DistrictAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'city'

    )


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
# Register your models here.

# class ProductsInline(admin.TabularInline):
#     model = Order.products.through

# class OrderAdmin(admin.ModelAdmin):
#     inlines = [ProductsInline,]
#     filter_horizontal = ('products',)

admin.site.register(City)
admin.site.register(Neighborhood, NeighborhoodAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Address)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PaymentMethod)
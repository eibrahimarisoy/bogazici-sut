from django.contrib import admin
from .models import City, Neighborhood, District, Address, \
    Customer, Category, Product, Order
# Register your models here.

class ProductsInline(admin.TabularInline):
    model = Order.products.through

class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductsInline,]
    filter_horizontal = ('products',)

admin.site.register(City)
admin.site.register(Neighborhood)
admin.site.register(District)
admin.site.register(Address)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)

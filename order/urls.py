from django.urls import path, include
from .views import index, add_customer, load_neighborhoodes, \
        customer, add_order, order, export_orders_xls, \
        add_district_and_neighborhood, add_product, products, \
        update_product, delete_product, update_customer, delete_customer, \
        delete_order, update_order, daily_order, search_status, CustomerAutocomplete
from django.conf.urls import url

urlpatterns = [
    path('', index, name="index"),
    path('add-customer/', add_customer, name="add_customer"),
    path('customer/', customer, name="customer"),
    path('update-customer/<int:id>/', update_customer, name="update_customer"),
    path('delete-customer/<int:id>/', delete_customer, name="delete_customer"),

    path('add-order/', add_order, name="add_order"),
    path('order/', order, name="order"),
    path('delete-order/<int:id>/', delete_order, name="delete_order"),
    path('update-order/<int:id>/', update_order, name="update_order"),

    path('add-product/', add_product, name="add_product"),
    path('products/', products, name="products"),
    path('update-product/<int:id>/', update_product, name="update_product"),
    path('delete-product/<int:id>/', delete_product, name="delete_product"),

    path('export-orders-xls/<str:date>/', export_orders_xls, name="export_orders_xls"),
    path('add-district-and-neighborhood/', add_district_and_neighborhood, name="add_district_and_neighborhood"),

        #ajax
    # path('ajax/load-townships/', load_townships, name='ajax_load_townships'),  
    path('ajax/load-neihgborhoodes/', load_neighborhoodes, name='ajax_load_neighborhoodes'),
    path('search-status/', search_status, name="search_status"),

    path('daily-order/<str:date>/', daily_order, name="daily_order"),

    url(
        r'^country-autocomplete/$',
        CustomerAutocomplete.as_view(),
        name='customer_autocomplete',
    ),
]

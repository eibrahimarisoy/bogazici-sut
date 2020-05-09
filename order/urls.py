from django.urls import path, include
from .views import index, add_customer, load_neighborhoodes, \
        customer, add_order, order, export_orders_xls, \
        add_district_and_neighborhood

urlpatterns = [
    path('', index, name="index"),
    path('add_customer/', add_customer, name="add_customer"),
    path('customer/', customer, name="customer"),

    path('add_order/', add_order, name="add_order"),
    path('order/', order, name="order"),

    path('export-orders-xls/<str:date>/', export_orders_xls, name="export_orders_xls"),
    path('add_district_and_neighborhood/', add_district_and_neighborhood, name="add_district_and_neighborhood"),

        #ajax
    # path('ajax/load-townships/', load_townships, name='ajax_load_townships'),  
    path('ajax/load-neihgborhoodes/', load_neighborhoodes, name='ajax_load_neighborhoodes'),  
]

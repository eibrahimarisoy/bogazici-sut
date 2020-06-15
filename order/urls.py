from django.conf.urls import url
from django.urls import include, path

from .views import (CustomerAutocomplete, add_customer, add_customer_from_file,
                    add_district_and_neighborhood, add_order, add_product,
                    ajax_customer_search, customer, customer_details,
                    daily_order, daily_revenue, delete_customer, delete_order,
                    delete_product, deliver_order, delivery_page,
                    download_customer_vcf, export_orders_xls, index,
                    load_neighborhoodes, number_of_customer_orders, order,
                    order_calendar, order_report, pay_with_eft,
                    payment_method_set, products, unpaid_orders,
                    update_customer, update_order, update_product)

urlpatterns = [
    path('', index, name="index"),
    path('add-customer/', add_customer, name="add_customer"),
    path('customer/', customer, name="customer"),
    path('customer/<str:sort_by>/', customer, name="customer"),

    path('update-customer/<int:id>/', update_customer, name="update_customer"),
    path('delete-customer/<int:id>/', delete_customer, name="delete_customer"),
    path('download-customer-vcf/<int:id>', download_customer_vcf, name="download_customer_vcf"),
    path('number-of-customer-orders/', number_of_customer_orders, name="number_of_customer_orders"),
    path('customer-details/<int:id>/', customer_details, name="customer_details"),

    path('add-order/', add_order, name="add_order"),
    path('add-order/<int:id>/', add_order, name="add_order"),
    path('order/', order, name="order"),
    path('delete-order/<int:id>/', delete_order, name="delete_order"),
    path('update-order/<int:id>/', update_order, name="update_order"),
    path('payment-method-set/<int:id>/<str:method>/', payment_method_set, name="payment_method_set"),
    path('unpaid-orders/', unpaid_orders, name="unpaid_orders"),
    path('pay-with-eft/<int:id>/', pay_with_eft, name="pay_with_eft"),
    path('order-calendar/', order_calendar, name="order_calendar"),
    path('daily-revenue/', daily_revenue, name="daily_revenue"),
    path('order-report/', order_report, name="order_report"),

    path('add-product/', add_product, name="add_product"),
    path('products/', products, name="products"),
    path('update-product/<int:id>/', update_product, name="update_product"),
    path('delete-product/<int:id>/', delete_product, name="delete_product"),

    path('export-orders-xls/<str:date>/', export_orders_xls, name="export_orders_xls"),
    path('add-district-and-neighborhood/', add_district_and_neighborhood, name="add_district_and_neighborhood"),
    path('add-customer-from-file/', add_customer_from_file, name="add_customer_from_file"),

    # ajax
    # path('ajax/load-townships/', load_townships, name='ajax_load_townships'),  
    path('ajax/load-neihgborhoodes/', load_neighborhoodes, name='ajax_load_neighborhoodes'),
    path('ajax-customer-search/', ajax_customer_search, name="ajax_customer_search"),

    path('daily-order/<str:date>/', daily_order, name="daily_order"),
    path('delivery-page/', delivery_page, name="delivery_page"),
    path('deliver-order/<int:id>/', deliver_order, name="deliver_order"),

    url(
        r'^customer-autocomplete/$',
        CustomerAutocomplete.as_view(),
        name='customer_autocomplete',
    ),
]

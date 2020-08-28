from django.conf.urls import url
from django.urls import include, path

from .views import (CustomerAutocomplete, add_customer, add_customer_from_file,
                    add_district_and_neighborhood, add_order, add_product,
                    ajax_customer_search, customer, customer_details,
                    daily_order, daily_revenue, delete_customer, delete_order,
                    delete_product, deliver_order, delivery_page,
                    download_customer_vcf, e_about, e_cart, e_category_details,
                    e_checkout, e_contact, e_index, e_product_details,
                    e_products, export_orders_xls, index, load_neighborhoodes,
                    number_of_customer_orders, order, order_calendar,
                    order_report, pay_with_eft, payment_method_set, products,
                    unpaid_orders, update_customer, update_order,
                    update_product, order_item_add, order_item_delete, order_item_update)

urlpatterns = [
    path('staff/', index, name="index"),
    path('staff/add-customer/', add_customer, name="add_customer"),
    path('staff/customer/', customer, name="customer"),
    path('staff/customer/<str:sort_by>/', customer, name="customer"),
    path('staff/update-customer/<int:id>/', update_customer, name="update_customer"),
    path('staff/delete-customer/<int:id>/', delete_customer, name="delete_customer"),
    path('staff/download-customer-vcf/<int:id>', download_customer_vcf, name="download_customer_vcf"),
    path('staff/number-of-customer-orders/', number_of_customer_orders, name="number_of_customer_orders"),
    path('staff/customer-details/<int:id>/', customer_details, name="customer_details"),
    path('staff/add-order/', add_order, name="add_order"),
    path('staff/add-order/<int:id>/', add_order, name="add_order"),
    path('staff/order/', order, name="order"),
    path('staff/delete-order/<int:id>/', delete_order, name="delete_order"),
    path('staff/update-order/<int:id>/', update_order, name="update_order"),
    path('staff/payment-method-set/<int:id>/<str:method>/', payment_method_set, name="payment_method_set"),
    path('staff/unpaid-orders/', unpaid_orders, name="unpaid_orders"),
    path('staff/pay-with-eft/<int:id>/', pay_with_eft, name="pay_with_eft"),
    path('staff/order-calendar/', order_calendar, name="order_calendar"),
    path('staff/daily-revenue/', daily_revenue, name="daily_revenue"),
    path('staff/order-report/', order_report, name="order_report"),

    path('staff/add-product/', add_product, name="add_product"),
    path('staff/products/', products, name="products"),
    path('staff/update-product/<int:id>/', update_product, name="update_product"),
    path('staff/delete-product/<int:id>/', delete_product, name="delete_product"),

    path('staff/export-orders-xls/<str:date>/', export_orders_xls, name="export_orders_xls"),
    path('staff/add-district-and-neighborhood/', add_district_and_neighborhood, name="add_district_and_neighborhood"),
    path('staff/add-customer-from-file/', add_customer_from_file, name="add_customer_from_file"),

    # ajax
    # path('ajax/load-townships/', load_townships, name='ajax_load_townships'),  
    path('ajax/load-neihgborhoodes/', load_neighborhoodes, name='ajax_load_neighborhoodes'),
    path('ajax-customer-search/', ajax_customer_search, name="ajax_customer_search"),

    path('staff/daily-order/<str:date>/', daily_order, name="daily_order"),
    path('staff/delivery-page/', delivery_page, name="delivery_page"),
    path('staff/deliver-order/<int:id>/', deliver_order, name="deliver_order"),

    url(
        r'^customer-autocomplete/$',
        CustomerAutocomplete.as_view(),
        name='customer_autocomplete',
    ),

    path('', e_index, name="e-index"),
    path('product-details/<int:id>/', e_product_details, name="e-product_details"),
    path('about/', e_about, name="e-about"),
    path('contact/', e_contact, name="e-contact"),
    path('products/', e_products, name="e-products"),
    path('category/<str:name>/', e_category_details, name="e-category_details"),
    path('cart/', e_cart, name="e-cart"),
    path('checkout/', e_checkout, name="e-checkout"),
    path('order-item-add/<int:product_id>/', order_item_add, name="order_item_add"),
    path('order-item-delete/<int:order_id>/<int:order_item_id>/', order_item_delete, name="order_item_delete"),
    path('oder-item-update/<int:item_id>/', order_item_update, name="order_item_update"),



]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('increase_quantity/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('change_order_status/<int:order_id>/', views.change_order_status, name='change_order_status'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('clear_session/', views.clear_session, name='clear_session'),
    path('process_checkout/', views.process_checkout, name='process_checkout'),
    path('qr_code/', views.qr_code, name='qr_code'),
  # URL pattern for the QR code page
    # path('order_status/', views.get_order_status, name='order_status'),
    # path('process_payment/', views.process_payment, name='process_payment'),

    # Add the URL patterns for the Rozer Pay and Paytm payment views
    path("payment/", views.order_payment, name="order_payment"),
    path("razorpay/callback/", views.callback, name="callback"),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('other_payment/', views.other_payment, name='other_payment'),
    path('about-us/', views.about_us, name='about_us'),
    path('process_upi_payment/', views.process_upi_payment, name='process_upi_payment'),

]

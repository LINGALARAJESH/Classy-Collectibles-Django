from django.urls import path,include
from . import views

urlpatterns = [
        path("",views.home,name="home"),
        path("purchase/",views.purchase,name="purchase"),
        path("checkout/",views.checkout,name="checkout"),
        path("orders/<str:email>",views.orders,name="orders"),
        path("success/<str:razorpay_payment_id>/<str:razorpay_order_id>/<str:razorpay_signature>",views.success,name="success"),
]

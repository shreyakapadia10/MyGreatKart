from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='PlaceOrder'),
    path('payment/', views.payment, name='Payment'),
    path('order-complete/', views.order_complete, name='OrderComplete'),
]
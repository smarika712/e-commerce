from django.urls import path
from . import views

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<slug:slug>/', views.cart_add, name='cart_add'),
    path('cart/remove/<slug:slug>/', views.cart_remove, name='cart_remove'),
]
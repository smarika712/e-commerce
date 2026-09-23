from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order/<uuid:order_id>/success/', views.order_success, name='order_success'),
    path('esewa/verify/', views.esewa_verify, name='esewa_verify'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),
    path(
    'khalti/callback/',
    views.khalti_callback,
    name='khalti_callback'
),
]
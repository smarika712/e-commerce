from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_detail, name='wishlist_detail'),
]
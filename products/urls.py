from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.product_create, name='product_create'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/edit/', views.product_update, name='product_update'),
    path('<slug:slug>/delete/', views.product_delete, name='product_delete'),
    path('search-suggestions/', views.product_search_suggestions, name='product_search_suggestions'),
]
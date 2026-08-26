from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('add/', views.product_create, name='product_create'),

    # Search must come before <slug:slug>/
    path('search/', views.product_search, name='product_search'),

    # Wishlist actions
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),

    path('<slug:slug>/edit/', views.product_update, name='product_update'),
    path('<slug:slug>/delete/', views.product_delete, name='product_delete'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
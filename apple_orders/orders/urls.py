from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("orders/new/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
]
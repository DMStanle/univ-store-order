from django.contrib import admin
from .models import Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["title_at_time_of_order", "price_at_time_of_order", "product"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "upc", "price", "is_active"]
    search_fields = ["title", "upc"]
    list_filter = ["category", "is_active"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer_name", "employee_name", "created_at", "total_before_tax"]
    search_fields = ["customer_name", "customer_school_id", "employee_name"]
    inlines = [OrderItemInline]
import base64
import io

import qrcode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderForm, ProductForm
from .models import Order, OrderItem, Product


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


@login_required
def home_redirect(request):
    return redirect("order_create")


@staff_required
def product_list(request):
    selected_category = request.GET.get("category", "")

    products = Product.objects.none()

    if selected_category in ["Mac", "iPad", "Apple Watch", "Other"]:
        products = Product.objects.filter(
            is_active=True,
            category=selected_category
        ).order_by("title")

    categories = ["Mac", "iPad", "Apple Watch", "Other"]

    return render(
        request,
        "orders/product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
        },
    )


@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "orders/product_form.html",
        {
            "form": form,
            "page_title": "Add Product",
        },
    )


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "orders/product_form.html",
        {
            "form": form,
            "page_title": "Edit Product",
        },
    )


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(
        request,
        "orders/product_confirm_delete.html",
        {"product": product},
    )


@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            selected_products = form.cleaned_data["products"]

            order = Order.objects.create(
                customer_name=form.cleaned_data["customer_name"],
                customer_phone=form.cleaned_data["customer_phone"],
                customer_email=form.cleaned_data["customer_email"],
                customer_school_id=form.cleaned_data["customer_school_id"],
                employee_name=form.cleaned_data["employee_name"],
                qr_data="0121224",
            )

            total = 0
            for product in selected_products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    title_at_time_of_order=product.title,
                    price_at_time_of_order=product.price,
                )
                total += product.price

            order.total_before_tax = total
            order.save(update_fields=["total_before_tax"])

            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm()

    grouped_products = {
        "Mac": Product.objects.filter(is_active=True, category="Mac").order_by("title"),
        "iPad": Product.objects.filter(is_active=True, category="iPad").order_by("title"),
        "Apple Watch": Product.objects.filter(is_active=True, category="Apple Watch").order_by("title"),
        "Other": Product.objects.filter(is_active=True, category="Other").order_by("title"),
    }

    return render(
        request,
        "orders/order_create.html",
        {
            "form": form,
            "grouped_products": grouped_products,
        },
    )


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(order.qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "qr_base64": qr_base64,
        },
    )
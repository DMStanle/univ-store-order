from django import forms
from .models import Order, Product
import re


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "model_number",
            "upc",
            "price",
            "category",
            "is_active",
        ]


class OrderForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def clean_customer_phone(self):
        phone = self.cleaned_data["customer_phone"]

        digits = re.sub(r"\D", "", phone)

        if len(digits) != 10:
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")

        formatted_phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return formatted_phone

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "customer_phone",
            "customer_email",
            "customer_school_id",
            "employee_name",
            "products",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["products"].queryset = Product.objects.filter(
            is_active=True
        ).order_by("category", "title")
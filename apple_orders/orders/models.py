from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Mac", "Mac"),
        ("iPad", "iPad"),
        ("Apple Watch", "Apple Watch"),
        ("Apple Care +", "Apple Care +"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=200)
    model_number = models.CharField(
        max_length=100,
        blank=True,
    )

    def clean(self):
        if self.category != "Apple Care +" and not self.model_number:
            raise ValidationError({
                "model_number": "Model number is required for this category."
            })

    upc = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Price before tax",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return f"{self.title} ({self.category})"


class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=30)
    customer_email = models.EmailField()
    customer_school_id = models.CharField(
    max_length=50,
    blank=True
)
    employee_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    total_before_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qr_data = models.CharField(max_length=255, default="Apple Order")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"

    def recalculate_total(self):
        total = sum(item.price_at_time_of_order for item in self.items.all())
        self.total_before_tax = total
        self.save(update_fields=["total_before_tax"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    title_at_time_of_order = models.CharField(max_length=200)
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title_at_time_of_order} - {self.price_at_time_of_order}"
import uuid
from django.conf import settings
from django.db import models
from products.models import Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_COD = 'cod'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Payment Failed'),
        (STATUS_COD, 'Cash on Delivery'),
    ]

    PAYMENT_COD = 'cod'
    PAYMENT_ESEWA = 'esewa'
    PAYMENT_KHALTI = 'khalti'

    PAYMENT_CHOICES = [
        (PAYMENT_COD, 'Cash on Delivery'),
        (PAYMENT_ESEWA, 'eSewa'),
        (PAYMENT_KHALTI, 'Khalti')
    ]
    khalti_pidx = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    khalti_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    esewa_transaction_uuid = models.CharField(max_length=100, blank=True, null=True, unique=True)
    esewa_ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
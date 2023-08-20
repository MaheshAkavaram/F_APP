from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_images', default='default_product_image.jpg')

    def total_quantity_in_carts(self):
        return CartItem.objects.filter(product=self).aggregate(total_quantity=models.Sum('quantity')).get('total_quantity') or 0

    def __str__(self):
        return self.name

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('other', 'other'),
        ('rozerpay', 'Rozer Pay'),  # Added 'rozerpay' as a new payment method
        # Add more payment methods here if needed
    )

    ADDRESS_CHOICES = (
        ('Chityala', 'Chityala'),
        ('Others', 'Others'),
    )

    ORDER_STATUS_CHOICES = (
        ('ordered', 'Ordered'),
        ('prepared', 'Prepared'),
        ('delivered', 'Delivered'),
    )

    user_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateField(default=timezone.now)
    order_time = models.TimeField(default=timezone.now)
    address_type = models.CharField(max_length=10, choices=ADDRESS_CHOICES)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        amount = self.product.price * self.quantity
        return f"Order #{self.pk} - {self.product.name} (Quantity: {self.quantity}, Amount: {amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product.name} - Quantity: {self.quantity}'

class QRCode(models.Model):
    image = models.ImageField(upload_to='qr_codes')

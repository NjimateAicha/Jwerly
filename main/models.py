from pyexpat.errors import messages
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# models.py
from django.conf import settings
from django.shortcuts import redirect, render



class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name
    

    
class About(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='about_images/')
    more_content = models.TextField(blank=True, null=True)  # Additional content for "Read More"

    def __str__(self):
        return self.title

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    sizes = models.CharField(max_length=200)  # Store sizes as a comma-separated string

    def final_price(self):
        """Calculate the final price after discount"""
        return self.price * (1 - self.discount / 100)
    def __str__(self):
        return self.name



class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()  # Nouveau champ pour l'email
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=(
        ('card', 'Pay by Card'),
        ('delivery', 'Pay on Delivery'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.name}"

    @property
    def total_quantity(self):
        return self.order_items.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    
    def ordered_products(self):
        return ", ".join([f"{item.quantity} x {item.product.name}" for item in self.order_items.all()])
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order #{self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'




class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"




class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



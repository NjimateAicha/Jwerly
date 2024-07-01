from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

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



class About(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='about_images/')
    more_content = models.TextField(blank=True, null=True)  # Additional content for "Read More"

    def __str__(self):
        return self.title


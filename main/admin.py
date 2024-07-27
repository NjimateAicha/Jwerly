
from django.contrib import admin


from .models import Category, Order, OrderItem, Payment, Product, About,Contact
from django.contrib import admin
from .models import Category, Product, About, Contact, Order, OrderItem, Payment
from main import models

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'category', 'stock', 'discount', 'sizes', 'image')
    list_filter = ('category',)  # Filtres sur la colonne catégorie
    search_fields = ('name',)  # Champ de recherche pour le nom du produit

    # Méthode pour afficher le nombre total de produits
    def get_total_products(self, request):
        return Product.objects.count()

    # Méthode pour afficher la somme totale des stocks disponibles
    def get_total_stock(self, request):
        return Product.objects.aggregate(total_stock=models.Sum('stock'))['total_stock']


class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'more_content', 'image')


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'message', 'created_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'phone_number', 'address',  'ordered_products','total_price', 'payment_method', 'created_at')
    list_filter = ('payment_method',)
    search_fields = ('user__username', 'name')
    inlines = [OrderItemInline]

    def ordered_products(self, obj):
        return obj.ordered_products()

    ordered_products.short_description = 'Ordered Products'  # Titre de la colonne dans l'admin

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'stripe_charge_id', 'amount', 'timestamp')

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(About, AboutAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment, PaymentAdmin)

from django.shortcuts import get_object_or_404, render

from .models import About, Category, Product

def home(request):
    return render(request, 'index.html')




def about(request):
    about_sections = About.objects.all()
    context = {
        'about_sections': about_sections,
    }
    return render(request, 'about.html', context)


# def jewellery(request):
#     all_products = Product.objects.all()
#     context = {
#         'all_products': all_products
#     }
#     return render(request, 'jewellery.html', context)


def jewellery(request):
    # Fetch all products
    all_products = Product.objects.all()
    
    context = {
        'all_products': all_products,
    }
    return render(request, 'jewellery.html', context)


def contact(request):
    return render(request, 'contact.html')

def panier(request):
    return render(request, 'panier.html')

def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category.html', context)


def index(request):
    categories = Category.objects.prefetch_related('products').all()
    trending_products = Product.objects.all()[:3] 
    special_ring = Product.objects.filter(category__name='Ring').first()
    # about_section = About.objects.all()
    about_sections = About.objects.all()
    
    context = {
        'trending_products': trending_products,
        'categories': categories,
        'special_ring': special_ring,
        'about_sections': about_sections,

    }
    return render(request, 'index.html', context)


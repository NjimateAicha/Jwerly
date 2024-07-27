import logging
from re import template
from venv import logger
from django import forms
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from django.db import transaction

from django.shortcuts import render, redirect
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views import View
from .models import Order, OrderItem, Payment
from django.core.mail import EmailMultiAlternatives
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

import stripe
from django.contrib.auth.decorators import login_required

from .models import About, Category, Contact, Order, OrderItem, Payment, Product
import stripe
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from django.views.decorators.http import require_POST

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail






stripe.api_key = settings.STRIPE_SECRET_KEY





def home(request):
    return render(request, 'index.html')

def payment(request):
    return render(request, 'payment.html')


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


def contactUs(request):
    return render(request, 'contactUs.html')

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




def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] < product.stock:
            cart[str(product_id)]['quantity'] += 1
            messages.success(request, 'Product quantity updated in cart.')
        else:
            messages.error(request, 'Not enough stock available.')
    else:
        if product.stock > 0:
            cart[str(product_id)] = {
                'id': product.id,
                'name': product.name,
                'price': float(product.final_price()),  # Convert DecimalField to float
                'quantity': 1,  # Initial quantity
                'image_url': product.image.url
            }
            messages.success(request, 'Product added to cart.')
        else:
            messages.error(request, 'Product out of stock.')

    request.session['cart'] = cart
    request.session.modified = True  # Assurez-vous de marquer la session comme modifiée

    return redirect('panier')  # Redirect to cart page after adding to cart


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = list(cart.values())
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    for item in cart_items:
        product = get_object_or_404(Product, pk=item['id'])
        item['stock'] = product.stock

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'panier.html', context)





def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        messages.success(request, 'Product removed from cart.')

    request.session['cart'] = cart
    return redirect('panier')

def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # obtenir la nouvelle quantité du formulaire
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            product = get_object_or_404(Product, pk=product_id)
            if product.stock >= quantity:
                cart[str(product_id)]['quantity'] = quantity
                messages.success(request, 'Product quantity updated in cart.')
            else:
                messages.error(request, 'Not enough stock available.')
            request.session['cart'] = cart
            request.session.modified = True  # Assurez-vous de marquer la session comme modifiée

    return redirect('panier')

@login_required
def admin_orders(request):
    orders = Order.objects.all()  # Récupérer toutes les commandes
    return render(request, 'admin/orders.html', {'orders': orders})











@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})



@login_required
def payment(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for item_id, item_data in cart.items():
        product = Product.objects.get(id=item_id)
        item = {
            'id': product.id,
            'name': product.name,
            'quantity': item_data['quantity'],
            'price': product.price,
            'image_url': product.image.url,
            'total_price': product.price * item_data['quantity']
        }
        cart_items.append(item)
        total_price += item['total_price']

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'payment.html', context)


# @login_required
# @transaction.atomic
# def process_order(request):
#     cart = request.session.get('cart', {})
#     cart_items = []
#     total_price = 0

#     for item_id, item_data in cart.items():
#         product = Product.objects.get(id=item_id)
#         item = {
#             'id': product.id,
#             'name': product.name,
#             'quantity': item_data['quantity'],
#             'price': product.price,
#             'image_url': product.image.url,
#             'total_price': product.price * item_data['quantity']
#         }
#         cart_items.append(item)
#         total_price += item['total_price']

#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             payment_option = request.POST.get('payment_option')

#             try:
#                 with transaction.atomic():
#                     # Payer par carte
#                     if payment_option == 'card':
#                         token = request.POST.get('stripeToken')
#                         if not token:
#                             form.add_error(None, "Le token Stripe est manquant")
#                             return render(request, 'order_confirmation.html', {'form': form, 'cart_items': cart_items, 'total_price': total_price})

#                         try:
#                             charge = stripe.Charge.create(
#                                 amount=int(total_price * 100),
#                                 currency='usd',
#                                 description='Paiement de la commande',
#                                 source=token,
#                             )
#                             payment_method = 'card'
#                         except stripe.error.StripeError as e:
#                             form.add_error(None, str(e))
#                             return render(request, 'order_confirmation.html', {'form': form, 'cart_items': cart_items, 'total_price': total_price})

#                         # Enregistrer les détails du paiement
#                         payment = Payment.objects.create(
#                             user=request.user,
#                             order=order,
#                             stripe_charge_id=charge.id,
#                             amount=total_price,
#                         )

#                     # Payer à la livraison
#                     elif payment_option == 'delivery':
#                         payment_method = 'delivery'
                    
#                     # Créer la commande
#                     order = Order.objects.create(
#                         user=request.user,
#                         name=form.cleaned_data['name'],
#                         address=form.cleaned_data['address'],
#                         phone_number=form.cleaned_data['phone_number'],
#                         email=email,
#                         total_price=total_price,
#                         payment_method=payment_method,
#                     )

#                     # Ajouter les produits commandés à la commande
#                     for item_id, item_data in cart.items():
#                         product = Product.objects.get(id=item_id)
#                         OrderItem.objects.create(
#                             order=order,
#                             product=product,
#                             quantity=item_data['quantity'],
#                             unit_price=product.price
#                         )

#                     # Effacer le panier de la session après la commande
#                     del request.session['cart']
#                     request.session.modified = True
#                       # Envoyer l'e-mail de confirmation de commande
#                     try:
#                         send_order_confirmation_email(order)
#                     except Exception as e:
#                         form.add_error(None, f"Erreur lors de l'envoi de l'e-mail de confirmation : {str(e)}")
#                         raise ValueError(f"Erreur lors de l'envoi de l'e-mail de confirmation : {str(e)}")

#                     # Rediriger vers une page de confirmation de commande
#                     return redirect('order_confirmation', order_id=order.id)

       

#             except stripe.error.CardError as e:
#                 form.add_error(None, e.error.message)
#             except Exception as e:
#                 form.add_error(None, str(e))
        
#     else:
#         form = PaymentForm()

#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'form': form,
#     }
#     return render(request, 'order_confirmation.html', context)
@login_required
@transaction.atomic
def process_order(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for item_id, item_data in cart.items():
        product = Product.objects.get(id=item_id)
        item = {
            'id': product.id,
            'name': product.name,
            'quantity': item_data['quantity'],
            'price': product.price,
            'image_url': product.image.url,
            'total_price': product.price * item_data['quantity']
        }
        cart_items.append(item)
        total_price += item['total_price']

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            payment_option = request.POST.get('payment_option')

            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        name=form.cleaned_data['name'],
                        address=form.cleaned_data['address'],
                        phone_number=form.cleaned_data['phone_number'],
                        email=email,
                        total_price=total_price,
                        payment_method='processing',
                    )

                    if payment_option == 'card':
                        token = request.POST.get('stripeToken')
                        charge = stripe.Charge.create(
                            amount=int(total_price * 100),
                            currency='usd',
                            description='Payment',
                            source=token,
                        )
                        payment_method = 'card'
                        Payment.objects.create(
                            user=request.user,
                            order=order,
                            stripe_charge_id=charge.id,
                            amount=total_price,
                        )
                        order.payment_method = payment_method
                        order.save()

                    elif payment_option == 'delivery':
                        order.payment_method = 'delivery'
                        order.save()

                    for item_id, item_data in cart.items():
                        product = Product.objects.get(id=item_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item_data['quantity'],
                            unit_price=product.price
                        )

                    del request.session['cart']
                    request.session.modified = True
                    send_order_confirmation_email(order)
                    return redirect('order_confirmation', order_id=order.id)

            except stripe.error.StripeError as e:
                form.add_error(None, str(e))
            except Exception as e:
                form.add_error(None, str(e))

    else:
        form = PaymentForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }
    return render(request, 'order_confirmation.html', context)




def send_order_confirmation_email(order):
    subject = 'Confirmation de commande'
    html_content = render_to_string('email.html', {'order': order})
    text_content = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    # Créer le message email
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
    except Exception as e:
        # Logger l'erreur ou la gérer comme nécessaire
        print(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")
        raise


class OrderForm(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=(
        ('card', 'Pay by Card'),
        ('delivery', 'Pay on Delivery'),
    ))

    # Ajoutez d'autres champs comme le nom, l'adresse, etc.

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    






class PaymentForm(forms.Form):
    name = forms.CharField(label='Name', required=True)
    address = forms.CharField(label='Address', widget=forms.Textarea(attrs={'rows': 4}), required=True)
    phone_number = forms.CharField(label='Phone Number', required=True)
    email = forms.EmailField(label='Email', required=True)




def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        email = request.POST.get('email')
        message = request.POST.get('message')
        phone = request.POST.get('phone')

        full_message = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                email,  # Adresse de l'expéditeur
                ['recipient-email@gmail.com'],  # Liste des destinataires
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            logger.error(f'Failed to send email. Error: {str(e)}')
            messages.error(request, f'Failed to send message. Error: {str(e)}')

        return redirect('contact')  # Redirection vers la page de contact après l'envoi

    return render(request, 'contactUs.html')

from django.db.models import Count
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Récupérer les produits similaires (optionnel, si nécessaire)
    similar_products = get_similar_products(product_id)
    
    # Enregistrer l'interaction dans la session (comme avant)
    viewed_products = request.session.get('viewed_products', [])
    if product_id not in viewed_products:
        viewed_products.append(product_id)
        request.session['viewed_products'] = viewed_products
        request.session.modified = True
    
    # Obtenir les produits recommandés basés sur les top 3 des commandes
    recommended_products = get_top_ordered_products()
    
    return render(request, 'product_detail.html', {
        'product': product, 
        'similar_products': similar_products,
        'recommendations': recommended_products
    })

def get_top_ordered_products(num_recommendations=3):
    top_products = OrderItem.objects.values('product_id').annotate(total_orders=Count('product_id')).order_by('-total_orders')[:num_recommendations]
    
    top_product_ids = [item['product_id'] for item in top_products]
    top_products = Product.objects.filter(id__in=top_product_ids)
    
    # Débogage
    print(f"Top ordered products: {top_products}")
    
    return top_products

def get_similar_products(product_id, num_recommendations=5):
    product = Product.objects.get(id=product_id)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:num_recommendations]
    return similar_products



class abc(View):
    def get(self, request):
        query = request.GET.get('q')
        products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
        return render(request, 'abc.html', {'products':products})
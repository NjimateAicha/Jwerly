"""
URL configuration for Pfa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django import views
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path


   # Assurez-vous que 'main' est bien le nom de votre application

from main import views



urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', views.index, name='index'),
  
    path('jewellery/', views.jewellery, name='jewellery'),
 
    path('contact-us/', views.contactUs, name='contactUs'),  # Nouvelle URL pour une autre vue de contact
    path('contact/', views.contact_view, name='contact'),   
   
    path('category/<int:category_id>/', views.category, name='category'),
    path('about/', views.about, name='about'),
    path('payment/', views.payment, name='payment'),
 
 
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('panier/', views.view_cart, name='panier'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('update_cart_quantity/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    path('payment/', views.payment, name='payment'),

    path('process_order/', views.process_order, name='process_order'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('abc/', views.abc.as_view(), name='abc'),
    
 
    
]
   
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
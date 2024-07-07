from django.shortcuts import render

from Products.models import Product


def home(request):
    products = Product.objects.all().order_by('-created_date')
    
    context = {
        'products':products,
    }
    return render(request, 'index.html',context)
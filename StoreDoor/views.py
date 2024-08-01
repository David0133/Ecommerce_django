from django.shortcuts import render

from Products.models import Product, ReviewRating



def home(request):
    products = Product.objects.all().order_by('-created_date')

    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id , status=True)
    
    context = {
        'products':products,
        'reviews':reviews
    }
    return render(request, 'index.html',context)
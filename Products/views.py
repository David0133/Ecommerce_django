

from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from Cart.models import CartItem
from Cart.views import _cart_id
from Products.forms import ReviewForm
from .models import Product, Category, ReviewRating, Variation, ProductGallery
from orders.models import OrderProduct

# Create your views here.

def product_detail(request,category_slug,product_slug):
    user = request.user
    if user.is_authenticated:
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug = product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
            variations = Variation.objects.filter(product=single_product)
            reviews = ReviewRating.objects.filter(product_id=single_product.id , status=True)
            
        
        except Exception as e:
            raise e

    else:
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug = product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
            variations = Variation.objects.filter(product=single_product)
            reviews = ReviewRating.objects.filter(product_id=single_product.id , status=True)
            if reviews:
                reviews = reviews
            else:
                reviews = None
            
        except Exception as e:
            raise e
    

    prodcutGallery = ProductGallery.objects.filter(product_id=single_product.id)
    print(single_product.variation_set.all())
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'variations':variations,
        'reviews':reviews,
        'prodcutGallery':prodcutGallery,
        'value' : True
        
    }
    
    return render(request, 'product-detail.html', context)


def products(request,category_slug=None):
    products = None
    categories = None
    
    if category_slug != None:
       categories = get_object_or_404(Category,slug=category_slug)
       products = Product.objects.filter(category=categories, is_available=True)
       paginator = Paginator(products,1)
       page = request.GET.get('page')
       paged_products = paginator.get_page(page)
       product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    context = {
        'products':paged_products,
        'product_count':product_count
    }
    return render(request,'products.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count
    }
    return render(request,'products.html',context)


@login_required(login_url='login')
def review(request,product_id):
    url = request.META.get('HTTP_REFERER')

    # Checking if user has purchased the product
    ordered = OrderProduct.objects.filter(user__id=request.user.id, product__id=product_id).exists()

    if ordered:
        if request.method == 'POST':
            try:
                reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
                form = ReviewForm(request.POST, instance=reviews)
                form.save()
                messages.success(request, 'Thank you your review has been Updated.')
                return redirect(url)
            except:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.review = form.cleaned_data['review']
                    data.rating = form.cleaned_data['rating']
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.product_id = product_id
                    data.user_id = request.user.id
                    data.save()
                    messages.success(request, 'Thank you your review has been submitted.')
                    return redirect(url)
    else:
        messages.error(request, 'You can review only purchased products.')
        return redirect(url)
    
    

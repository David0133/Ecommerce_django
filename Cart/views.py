from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from Products.models import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from orders.forms import OrderForm
# Create your views here.

def _cart_id(request):
    
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                try:
                    variation = Variation.objects.get(product=product, variation_value__iexact=value,variation_category__iexact=key)
                    product_variation.append(variation)
                except:
                    pass 

        # implementing variation with the cart functionality
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()  
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            # existing variation -> database
            # current variation -> product_variation
            # item_id -> database
            
            # existing variation list
            ex_var_list = []
            # cart item id list
            id = []
            
            # check current variation inside the existing variation - increase quantity for cart_item
            for item in cart_item:
                # print(item)
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation)) # existing_variation into list
                id.append(item.id) # appending item id in list
            if product_variation in ex_var_list:
                # increase the cart item qunatity
                
                # id from the list
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
                
            else:
                # item creation
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                
                # create new cart item
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(product = product, quantity = 1, user=current_user)
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
    
        return redirect('cart')
     # If user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    # print(variation)
                    product_variation.append(variation)
                except:
                    pass 

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except (TypeError,Cart.DoesNotExist):
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()  
        
        # implementing variation with the cart functionality
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()    
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation -> database
            # current variation -> product_variation
            # item_id -> database
            
            # existing variation list
            ex_var_list = []
            # cart item id list
            id = []
            
            # check current variation inside the existing variation - increase quantity for cart_item
            for item in cart_item:
                # print(item)
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation)) # existing_variation into list
                id.append(item.id) # appending item id in list
            
            # print(ex_var_list)
            # print(ex_var_list[1])
            # print(product_variation)
            
            if product_variation in ex_var_list:
                # increase the cart item qunatity
                
                # id from the list
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
                
            else:
                # item creation
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                
                # create new cart item
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(product = product, quantity = 1, cart = cart)
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # close()
        return redirect('cart')


def remove_cart(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    current_variation = []
    color = request.GET.get('color')
    size = request.GET.get('size')
    current_variation.append(color)
    current_variation.append(size)
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user = request.user)
        for item in cart_item:
            existing_variation = item.variation.all()
            if existing_variation.filter(variation_value__iexact = current_variation[0]).exists() and existing_variation.filter(variation_value__iexact = current_variation[1]).exists():
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save()
                else:
                    item.delete()
                    break
   
    return redirect('cart')

def remove_cart_item(request, product_id):
    current_variation = []
    current_variation.append(request.GET.get('color'))
    current_variation.append(request.GET.get('size'))
    
    product = get_object_or_404(Product, id=product_id)
    print(product,"None")
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user =request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.filter(product=product , cart=cart)
    for item in cart_item:
        existing_variation = item.variation.all()
        if existing_variation.filter(variation_value__iexact = current_variation[0]).exists() and existing_variation.filter(variation_value__iexact = current_variation[1]).exists():
            item.delete()
            break
        
    # cart_item.delete()
    return redirect('cart')
     



        
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            if Cart.objects.filter(cart_id = _cart_id(request)).exists() == False:
                cart = Cart.objects.create(cart_id = _cart_id(request))
                cart.save()
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        
    }
          
    return render(request, 'cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    form = OrderForm()
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'form':form
    }
    return render(request, 'checkout.html', context)

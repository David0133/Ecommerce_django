import datetime
from django.core.mail import EmailMessage
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from Cart.models import *
from .forms import *



def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered = False, order_number= body['orderID'])
    # Store transaction details inside PAYMENT model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    print("payment saved")
    # Update ORDER model 
    order.payment = payment
    order.is_ordered = True
    order.save()
    # Move the cart items to the Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        # ManytoManyField needs to be saved first
        order_product.save()
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()


    # Decrement the quantity of the available stock

    product = Product.objects.get(id=item.product_id)
    product.stock -= item.quantity
    product.save()

    # CLEAR the cart 
    
    CartItem.objects.filter(user=request.user).delete()

    # SEND order EMAIL to customer
    
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })

    to_email = request.user.email 
    send_email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
    send_email.send()

    # SEND order number and transaction id to sendData method via JSON1

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)
    # return render(request, 'payments.html')

def place_order(request):
    current_user = request.user
    
    # if cart count is zero, then redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    tax = 0
    grand_total = 0
    total = 0
    quantity = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (2 * total)/100
    grand_total = total + tax

    if cart_count <= 0:
        return redirect('store') 
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            # Store all the billing information inside the Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data.get('first_name')
            data.last_name = form.cleaned_data.get('last_name')
            data.phone = form.cleaned_data.get('phone')
            data.email = form.cleaned_data.get('email')
            data.address_line_1 = form.cleaned_data.get('address_line_1')
            data.address_line_2 = form.cleaned_data.get('address_line_1')
            data.country = form.cleaned_data.get('country')
            data.state = form.cleaned_data.get('state')
            data.city = form.cleaned_data.get('city')
            data.order_note = form.cleaned_data.get('order_note')
            data.order_total = grand_total
            data.tax = tax
            data.status = 'New'
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number 202407032
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d') 
            order_number = current_date + str(data.id)  # 20210525
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'payments.html', context)

    form = OrderForm()
    context = {
        'order' :order,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'form': form
    }
    
    return render(request,'place-order.html', context)



def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order=order)
    subTotal = 0
    tax = 0
    grand_total = 0
    for i in ordered_products:
        subTotal += i.product.price * i.quantity
        tax = (2 * subTotal)/100
        grand_total = subTotal + tax
    context = {
        'order': order,
        'transID': transID,
        'ordered_products': ordered_products,
        'subTotal': subTotal,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request,'orders/order_complete.html',context)

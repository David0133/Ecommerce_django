
# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect

from Cart.models import Cart, CartItem
from Cart.views import _cart_id
from orders.models import Order, OrderProduct

from .forms import *
from .models import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

def register(request):
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username = email.split('@')[0]
            if Account.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('login')
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save() 
            
            # User Activation

            current_site = get_current_site(request)
            print(current_site)
            mail_subject = 'Please activate your account'
            message = render_to_string('userAccount/account_varification.html', {
                'user':user, # user object itself
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # to hide primary key of user
                'token':default_token_generator.make_token(user),                
            })
            
            to_email = email
            send_email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
            send_email.send()


            messages.success(request, 'Registration Successfull !')
            return redirect('/accounts/login/?command=verification&email='+email)
            
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'userAccount/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation =[]

                     # getting the product variations by cart id
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                    
                    # get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    # cart item id list
                    id = []
            
                    # check current variation inside the existing variation - increase quantity for cart_item
                    for item in cart_item:
                        # print(item)
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation)) # existing_variation into list
                        id.append(item.id) # appending item id in list
                                
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                            
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            # messages.success(request, "You are now logged in.")
            # HTTP_REFERER is used to get the previous url it is in the request.META dictionary
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next = /cart/checkout/
                print('Query: ', query)
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'userAccount/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Your are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):
    user = Account.objects.get(id=request.user.id)
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    count = orders.count()
    ordered = OrderProduct.objects.filter(user_id=request.user.id)

    user_profile = UserProfile.objects.get(user_id=request.user.id)
    

    return render(request, 'userAccount/dashboard.html',{'orders':orders,'ordered':ordered,'user':user,'count':count,'user_profile':user_profile})

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) # exact is case sensitive
            
            # reset password logic
            current_site = get_current_site(request)
            mail_subject = 'Reset your account'
            message = render_to_string('userAccount/reset_password_email.html', {
                'user':user, # user object itself
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # to hide primary key of user
                'token':default_token_generator.make_token(user),                
            }) 
            to_email = email
            send_email = EmailMessage(mail_subject, body=message, to=[to_email])
            send_email.send()
            messages.success(request, "Password reset email has been sent to your email address.")
            return redirect('login')
        else:
            messages.error(request, "Account doesn't exits !")
            return redirect('forgotPassword')
    return render(request, 'userAccount/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    
    else:
        messages.error(request, "This link is expired")
        return redirect('login')
    
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, "Password doesn't match !")
            return redirect('resetPassword')
    else:    
        return render(request, 'userAccount/resetPassword.html')
    


def myOrders(request):
    orders = Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context = {
        "orders":orders
    }
    return render(request,'orders/my_orders.html',context)

def edit_profile(request):
    user_profile = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request,"Your Profile has been updated")
            return redirect('edit_profile')
    else:
        
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'user_profile':user_profile,
    }
    return render(request,'userAccount/edit_profile.html',context=context)


def changePassword(request):
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')
        try:
            user = Account.objects.get(username__exact=request.user.username)
        except:
            messages.error(request, 'User does not exist')
            return redirect('login')
        

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('login')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'new password and confirm password does not match')
            return redirect('change_password')
    return render(request,'userAccount/changePassword.html')

@login_required(login_url='login')
def orderDetail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id,user=request.user)
    order = Order.objects.get(order_number = order_id,user=request.user)
    print(order_detail.first())
    context ={
        'ordered_products':order_detail,
        'order':order
    }
    return render(request,'orders/order_detail.html',context)
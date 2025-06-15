from django.shortcuts import render,redirect
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .form import ContactForm


import datetime
import json
from .models import *
from .utils import cookieCart, cartData, guestOrder
# Create your views here.
def store(request):
     data = cartData(request)
     # cartItems = data ['cartItems']
     query = request.GET.get('query')
     if query:
        products = Product.objects.filter(name__icontains=query)
     else:
        products = Product.objects.all()

     context = {
        'products': products,
        'cartItems': cartData(request)['cartItems'],  }# Assuming you use cartData()
     # products= Product.objects.all()
     # context = {'products': products,'cartItems':cartItems}
     return render(request, 'store/store.html', context)

def about(request):
    data = cartData(request)
    cartItems = data ['cartItems']
    context = {'cartItems':cartItems}
    return render(request, 'store/about.html', context)

def contact(request):
    data = cartData(request)
    cartItems = data ['cartItems']
    context = {'cartItems':cartItems}
    
    
    return render(request, 'store/contact.html',  context)

def login_view(request):
    data = cartData(request)
    cartItems = data ['cartItems']
    context = {'cartItems':cartItems}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')  # Redirect to home
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
     
    return render(request, 'store/login.html', context)

def logout_view(request):
    data = cartData(request)
    cartItems = data ['cartItems']
    context = {'cartItems':cartItems}
    logout(request)
    return render(request, 'store/logout.html', context)

# def logout_view(request):
#     logout(request)
#     return redirect('store')  # or your homepage view name

def cart(request):
     data = cartData(request)
     cartItems = data ['cartItems']
     order = data ['order']
     items = data ['items']

     context = {'items':items, 'order': order,'cartItems':cartItems}
     return render(request, 'store/cart.html', context)

# from django.views.decorators.csrf import csrf_exempt


def checkout(request):
     
     data = cartData(request)
     cartItems = data ['cartItems']
     order = data ['order']
     items = data ['items']

     context = {'items':items, 'order': order,'cartItems':cartItems}
     return render(request, 'store/checkout.html', context)

def updateItem(request):
     data=json.loads(request.body)
     productId = data['productId']
     action = data['action']
     print('Action:', action)
     print('Product:', productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)

     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

     if action == 'add':
          orderItem.quantity = (orderItem.quantity + 1)
     elif action == 'remove':
          orderItem.quantity = (orderItem.quantity - 1)

     orderItem.save()

     if orderItem.quantity <= 0:
          orderItem.delete()
     return JsonResponse('Item was addes',safe=False)

from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
          
     else:
          customer,order= guestOrder(request,data)
     total = float(data['form']['total'])
     order.transaction_id = transaction_id

     if total == order.get_cart_total:
          order.complete = True
     order.save()

     if order.shipping == True:
          ShippingAddress.objects.create(
          customer=customer,
          order=order,
          address=data['shipping']['address'],
          city=data['shipping']['city'],
          state=data['shipping']['state'],
          zipcode=data['shipping']['zipcode'],
          )

     return JsonResponse('Payment submitted..', safe=False)

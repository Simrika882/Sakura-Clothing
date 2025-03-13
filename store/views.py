from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from store.models import Order, OrderItem, Invoice, ShippingAddress, Product, Category ,Customer # Ensure all necessary models are imported
from store.utils import cookieCart, cartData, guestOrder
from userauths.forms import SearchForm
from django.db.models import Q
from django.urls import reverse

def index(request):
    data = cartData(request)
    cartItems = data['cartItems']
    return render(request, 'store/index.html', {'cartItems': cartItems})

def category_view(request, category_name):
    data = cartData(request)
    cartItems = data['cartItems']

    category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=category)
    context = {'products': products, 'category': category, 'cartItems': cartItems}
    return render(request, 'store/category.html', context)

def clothes(request):
    data = cartData(request)
    cartItems = data['cartItems']

    category = get_object_or_404(Category, name='clothes')
    products = Product.objects.filter(category=category)        
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/clothes.html', context)

def jeans(request):
    data = cartData(request)
    cartItems = data['cartItems'] 

    category = get_object_or_404(Category, name='jeans')
    products = Product.objects.filter(category=category)       
    context = {'products': products, 'cartItems': cartItems} 
    return render(request, 'store/jeans.html', context)

def shoes(request):
    data = cartData(request)
    cartItems = data['cartItems']

    category = get_object_or_404(Category, name='shoes')
    products = Product.objects.filter(category=category)        
    context = {'products': products, 'cartItems': cartItems}    
    return render(request, 'store/shoes.html', context)

def accessories(request):
    data = cartData(request)
    cartItems = data['cartItems']

    category = get_object_or_404(Category, name='accessories')  # Corrected category name
    products = Product.objects.filter(category=category)     
    context = {'products': products, 'cartItems': cartItems}    
    return render(request, 'store/accessories.html', context)

def search(request):
    form = SearchForm()
    results = []
    
    data = cartData(request)
    cartItems = data['cartItems']

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            if len(query) >= 4:
                results = Product.objects.filter(
                    Q(name__istartswith=query) | Q(name__icontains=query)
                )

    return render(request, 'store/search.html', {'form': form, 'results': results, 'cartItems': cartItems})

def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product= product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    if request.method == 'POST':
        try:
            transaction_id = datetime.datetime.now().timestamp()
            data = json.loads(request.body)

            if request.user.is_authenticated:
                customer = request.user.customer
                order, created = Order.objects.get_or_create(customer=customer, complete=False)
            else:
                customer, order = guestOrder(request, data)

            total = float(data['form']['total'])
            order.transaction_id = transaction_id

            if total == order.get_cart_total:
                order.complete = True
            order.save()

            if order.shipping:
                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],
                )

            # Create the invoice
            invoice = Invoice.objects.create(
                order=order,
                customer=customer,
                total_amount=order.get_cart_total
            )

            # Generate the URL for the invoice view
            invoice_url = reverse('invoice_view', args=[invoice.id])
            return JsonResponse({'url': invoice_url}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'store/invoice.html', {'invoice': invoice})


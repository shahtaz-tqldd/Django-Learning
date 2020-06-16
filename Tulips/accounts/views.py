from django.shortcuts import render, redirect
from .models import *
from .forms import OrderForm 
from django.forms import inlineformset_factory

# Create your views here.

def home(request):
	customer = Customer.objects.all()
	orders = Order.objects.all()

	total_orders = orders.count()
	orders_delivered = orders.filter(status = 'Delivered').count()
	orders_pending = orders.filter(status = 'Pending').count()

	context = {'customer': customer, 'orders':orders , 'total_orders': total_orders, 
			'orders_delivered': orders_delivered, 'orders_pending': orders_pending }

	return render(request, 'accounts/homepage.html', context)

def products(request):
	all_products = Product.objects.all()

	context = {'products_list': all_products}
	return render(request, 'accounts/products.html', context)

def customer(request, pk):
	customer = Customer.objects.get(id = pk)
	order = customer.order_set.all()
	order_count = order.count()

	context = {'customer': customer, 'order': order, 'order_count': order_count}

	return render(request, 'accounts/customer.html', context)

def createOrder(request, pk):

	OrderFormSet = inlineformset_factory(Customer, Order, fields = ('products', 'status'), extra = 6)

	customer = Customer.objects.get(id = pk)
	
	formset = OrderFormSet(queryset = Order.objects.none(), instance = customer)
	#form = OrderForm(initial = {'customer':customer})

	if request.method == 'POST':
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'formset': formset}
	return render(request, 'accounts/order_form.html', context)

def updateOrder(request, pk):

	order = Order.objects.get(id=pk)
	form = OrderForm(instance = order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance = order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form': form}
	return render(request, 'accounts/order_form.html', context)

def deleteOrder(request, pk):
	
	order = Order.objects.get(id = pk)

	if request.method == 'POST':
		order.delete()
		return redirect('/')

	context = {'item':order}
	return render(request, 'accounts/delete_order.html', context)

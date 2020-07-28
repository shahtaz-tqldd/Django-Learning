from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import *
from .form import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users, admin_only



@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username = username, password = password)

		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Username or Password is incorrect')	

	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('loginPage')


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['customer'])
def UserPage(request):
	orders = request.user.customer.order_set.all()
	
	total_orders = orders.count()
	delivered = orders.filter(status = 'Delivered').count()
	pending = orders.filter(status = 'Pending').count()

	print('ORDERS:', orders)

	context = {'orders': orders, 'total_orders': total_orders, 'delivered': delivered, 'pending': pending}
	return render(request, 'accounts/user.html', context)


@unauthenticated_user
def registerPage(request):
	form = CreateUserForm()

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			messages.success(request, 'Account has been created successfully for ' + username)
			return redirect('loginPage')

	context = {'form':form}
	return render(request, 'accounts/register.html', context)	

@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['customer','admin'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()


	context = {'form':form}
	return render(request, 'accounts/account_settings.html', context)


@login_required(login_url = 'loginPage')
#@allowed_users(allowed_roles=['admin'])
@admin_only
def home(request):
	orders = Order.objects.all()
	customer = Customer.objects.all()

	total_customer = customer.count()

	total_orders = orders.count()
	delivered = orders.filter(status = 'Delivered').count()
	pending = orders.filter(status = 'Pending').count()

	context = {'orders': orders , 'customers': customer, 'total_customer': total_customer, 
				'total_orders': total_orders, 'delivered': delivered, 'pending': pending}

	return render(request, 'accounts/homepage.html' , context)


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()

	return render(request, 'accounts/products.html' , {'products': products})


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
	customer = Customer.objects.get(id = pk)
	orders = customer.order_set.all()
	order_count = orders.count()
	myFilter = OrderFilter(request.GET, queryset = orders)
	orders = myFilter.qs 

	context = {'customer': customer, 'orders': orders, 'orders_count': order_count, 'myFilter': myFilter}

	return render(request, 'accounts/customer.html', context)	


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields =('product', 'status'), extra = 10)
	customer = Customer.objects.get(id = pk)
	formset = OrderFormSet(queryset = Order.objects.none(), instance = customer)
	#form = OrderForm(initial = {'customer':customer})

	if request.method == 'POST':
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance = customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'formset': formset}

	return render(request, 'accounts/order_form.html', context)	


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['admin'])
def	updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance = order)
	context = {'form': form}

	if request.method == 'POST':
		form = OrderForm(request.POST, instance = order)
		if form.is_valid():
			form.save()
			return redirect('/')	

	return render(request, 'accounts/order_form.html', context)


@login_required(login_url = 'loginPage')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id = pk)

	if request.method == 'POST':
		order.delete()
		return redirect('/')

	context = {'item': order}

	return render(request, 'accounts/delete_order.html', context)	
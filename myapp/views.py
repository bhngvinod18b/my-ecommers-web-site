from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Employee, Manager, Add_product, Customer_profile, Book_product


# PUBLIC HOME
from .models import UserProfile

def home(request):
    if not request.user.is_staff:
        return redirect('customer_home')
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('manager_dashboard')
    products = Add_product.objects.all().order_by('-id')

    return render(request, 'home.html', {
        'products': products
    })

# USER HOME
@login_required
def user_home(request):
    return render(request, 'user_home.html')


# MANAGER DASHBOARD
from django.contrib.auth.models import User

@login_required
def manager_dashboard(request):

    if not request.user.is_staff:
        return redirect('user_home')

    all_users = User.objects.all().order_by('-id')
    all_products = Add_product.objects.all().order_by('-id')
    all_orders = Book_product.objects.all().order_by('-created_at')

    context = {
        'all_users': all_users,
        'all_products': all_products,
        'all_orders': all_orders
    }

    return render(request, 'manager_dashboard.html', context)
@login_required
def update_status(request, order_id):
    order = get_object_or_404(Book_product, id=order_id)

    if request.method == "POST":
        order.status = request.POST.get('status')
        order.save()

    return redirect('manager_dashboard')

@login_required
def add_employe(request):

    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role='employee'
        )

        return redirect('manager_dashboard')

    return render(request, 'add_employee.html')

@login_required
def manager_profile(request):

    if not request.user.is_staff:
        return redirect('user_home')

    if request.method == 'POST':

        phone = request.POST.get('phone')

        if phone:

            Manager.objects.create(
                phone=phone
            )

            return redirect('manager_dashboard')

    return render(request, 'manager_profile.html')


@login_required
def product_add(request):

    if request.method == 'POST':

        product = request.POST.get('product')
        quantity = request.POST.get('quantity')
        catogery = request.POST.get('catogery')
        price = request.POST.get('price')

        if product and quantity and catogery and price:

            Add_product.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                catogery=catogery,
                price=price
            )

            return redirect('manager_dashboard')

    return render(request, 'product.html')


@login_required
def customer(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        gmail = request.POST.get('gmail')
        adress = request.POST.get('adress')

        if name and phone and gmail and adress:

            Customer_profile.objects.create(
                user=request.user,
                phone=phone,
                gmail=gmail,
                adress=adress
            )

            return redirect('customer_dashboard')

    return render(request, 'customer.html')
from django.db.models import Sum

@login_required
def customer_dashboard(request):

    my_orders = Book_product.objects.filter(user=request.user).order_by('-id')

    myprofile = Customer_profile.objects.filter(user=request.user).first()

    # ✅ GRAND TOTAL (FIX)
    total_amount = my_orders.aggregate(
        Sum('total_price')
    )['total_price__sum'] or 0

    return render(request, 'customer_dashboard.html', {
        'myprofile': myprofile,
        'my_orders': my_orders,
        'total_amount': total_amount
    })
@login_required
def delete_my_orders(request, id):
    my_order = get_object_or_404(Book_product, user=request.user, id=id)
    if request.method == 'POST':
        my_order.delete()
        return redirect('customer_dashboard')
    
    
    
    
    
from django.db.models import Q
from .models import Add_product

@login_required
def customer_home(request):

    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')

    all_products = Add_product.objects.all().order_by('-id')

    # 🔍 search filter
    if search_query:
        all_products = all_products.filter(
            Q(product__icontains=search_query)
        )

    # 📂 category filter
    if category:
        all_products = all_products.filter(catogery=category)

    # ✅ dynamic categories for dropdown
    categories = Add_product.objects.values_list('catogery', flat=True).distinct()

    return render(request, 'customer_home.html', {
        'all_products': all_products,
        'categories': categories,
        'search_query': search_query,
        'category': category
    })
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from .models import Add_product, Book_product
@login_required
def place_order(request, id):

    product = get_object_or_404(Add_product, id=id)

    if request.method == "POST":

        qty = int(request.POST.get('quantity'))
        address = request.POST.get('address')

        if qty > product.quantity:
            messages.error(request, "Not enough stock")
            return redirect('place_order', id=id)

        with transaction.atomic():

            product = Add_product.objects.select_for_update().get(id=id)

            if qty > product.quantity:
                messages.error(request, "Not enough stock")
                return redirect('place_order', id=id)

            Book_product.objects.create(
                product=product,
                user=request.user,
                quantity=qty,
                address=address
            )

            product.quantity -= qty
            product.save()

        return redirect('succes_page')

    return render(request, 'place_order.html', {
        'product': product
    })

@login_required
def book(request, id):

    product = get_object_or_404(
        Add_product,
        id=id
    )

    if request.method == 'POST':

        qty = int(
            request.POST.get('quantity') or 1
        )

        try:

            with transaction.atomic():

                # LOCK PRODUCT ROW
                product = (
                    Add_product.objects
                    .select_for_update()
                    .get(id=id)
                )

                # CHECK STOCK
                if qty > product.quantity:

                    messages.error(
                        request,
                        "Not enough stock available"
                    )

                    return redirect('book', id=id)

                # CREATE BOOKING
                Book_product.objects.create(
                    product=product,
                    user=request.user,
                    quantity=qty
                )

                # REDUCE STOCK
                product.quantity -= qty

                product.save()

            messages.success(
                request,
                "Product booked successfully"
            )

            return redirect('succes_page')

        except Exception as e:

            messages.error(
                request,
                str(e)
            )

    return render(request, 'book.html', {
        'product': product
    })
@login_required
def bk(request, id):
    product = get_object_or_404(Add_product, id=id)

    if request.method == 'POST':
        qty = request.POST.get('quantity') or 1

        Book_product.objects.create(
            product=product,
            user=request.user,
            quantity=int(qty)
        )

        return redirect('succes_page')

    return render(request, 'book.html', {'product': product})
@login_required
def succes_page(request):
    return render(request, 'succes.html')
@login_required
def my_bookings(request):
    bookings = Book_product.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'booking.html', {'bookings': bookings})
# LOGIN
def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


# LOGOUT
def user_logout(request):
    logout(request)
    return redirect('login')


# REGISTER
def register(request):

    from django.contrib.auth.forms import UserCreationForm

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        user = form.save()

        UserProfile.objects.create(
            user=user,
            role='customer'
        )

        login(request, user)

        return redirect('customer_home')

    return render(request, 'register.html', {'form': form})
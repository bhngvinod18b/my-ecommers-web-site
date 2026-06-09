from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Employee, Manager, Add_product, Customer_profile, Book_product, Notifications


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
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
    f"user_{order.user.id}",
    {
        "type": "send_status_update",
        "message": f"Your order #{order.id} status updated to {order.status}"
    }
)
    return redirect('manager_dashboard')
# views.py
login_required
@login_required
def update_status_quick(request, order_id):
    order = get_object_or_404(Book_product, id=order_id)

    if request.method == "POST":
        status = request.POST.get('status')
        if status in ['pending', 'confirmed', 'cancelled']:
            order.status = status
            order.save()
            return redirect('my_worklist')

    return render(request, 'update.html', {'item': order})
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

            Manager.objects.get_or_create(
                user=request.user,
                phone=phone
            )

            return redirect('manager_dashboard')

    return render(request, 'manager_profile.html')
@login_required
def top_selling_product(request):
    top_selling = Book_product.objects.values('product__product',
            'product__price').annotate(total_sold = Sum('quantity')).order_by('-total_sold')
    return render(request, 'top_selling.html', {'top_selling': top_selling})

@login_required
def product_add(request):

    if request.method == 'POST':

        product = request.POST.get('product')
        quantity = request.POST.get('quantity')
        category = request.POST.get('catogery')
        price = request.POST.get('price')

        if product and quantity and category and price:

            Add_product.objects.create(
                users=request.user,
                product=product,
                quantity=quantity,
                catogery=category,
                price=price
            )
            

            # send to ALL customers
            customers = Customer_profile.objects.all()
            for customer in customers:
                Notifications.objects.create(
                    sender=request.user,
                    reciver=customer.user,
                    content=f'{request.user.username} added {product}'
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
        product_name = my_order
        order_id = id
        username = request.user
        my_order.delete()
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "manager_notifications",
            {
                "type": "send_order_notification",
                "message": f"❌ Order #{order_id} deleted by {username} ({product_name})"
            }
        )
        
    
        return redirect('customer_dashboard')
    
from django.db.models import Q
from .models import Add_product
from django.core.paginator import Paginator

from django.core.paginator import Paginator
from django.db.models import Q

def customer_home(request):
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')

    products = Add_product.objects.all()

    if search_query:
        products = products.filter(product__icontains=search_query)

    if category:
        products = products.filter(catogery=category)

    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer_home.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'category': category,
        'categories': Add_product.objects.values_list('catogery', flat=True).distinct()
    })

@login_required
def product_availability(request):
    all_products = Add_product.objects.all().order_by('-id')
    search_query = request.GET.get('search', '')
    if search_query:
        all_products = all_products.filter(
            Q(product__icontains=search_query)|
            Q(product__icontains=search_query)
        )
    return render(request, 'product_availability.html',
                  {'all_products': all_products, 'search_query': search_query})
        

from django.db import transaction

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Add_product, Book_product, Wishlist


@login_required
def place_order(request, id):

    product = get_object_or_404(Add_product, id=id)

    if request.method == "POST":

        qty = int(request.POST.get('quantity', 0))
        address = request.POST.get('address')

        if qty <= 0:
            messages.error(request, "Invalid quantity")
            return redirect('place_order', id=id)

        with transaction.atomic():

            product = Add_product.objects.select_for_update().get(id=id)

            if qty > product.quantity:
                messages.error(request, "Not enough stock")
                return redirect('place_order', id=id)

            # create order
            order = Book_product.objects.create(
                product=product,
                user=request.user,
                quantity=qty,
                address=address
            )

            # reduce stock
            product.quantity -= qty
            product.save()

        # -------------------------------
        # WebSocket notification
        # -------------------------------
        print("🔥 Sending WebSocket notification...")

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "manager_notifications",
            {
                "type": "send_order_notification",
                "message": f"New order #{order.id} placed by {request.user.username} for {product.product}"
            }
        )

        print("✅ WebSocket message sent")

        return redirect('succes_page', id=product.id)

    return render(request, 'place_order.html', {
        'product': product
    })
@login_required
def inbox(request):
    all_notification = Notifications.objects.filter(reciver=request.user).all().order_by('-id')
    return render(request, 'notification.html', {'all_notification': all_notification})
def succes_page(request, id):
    product = get_object_or_404(Add_product, id=id)
    return render(request, 'succes.html', {'product': product})
@login_required
def my_bookings(request):
    bookings = Book_product.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'booking.html', {'bookings': bookings})
from .models import Rating
@login_required
def give_rating(request, id):
    product = get_object_or_404(Add_product, id=id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        if rating and review:
            Rating.objects.create(
                product=product, rating=int(rating), review=review, user=request.user
                
            )
            return redirect('customer_dashboard')
    return render(request, 'rating.html', {'product': product})
from django.db.models import Avg
@login_required
def product_detail_page(request, id):
    product = get_object_or_404(Add_product, id=id)
    avg_rating = Rating.objects.filter(product=product).aggregate(
        Avg('rating')
    )['rating__avg']
    return render(request, 'detail.html', {
        'product': product,
        'avg_rating': avg_rating
    })
            
@login_required
def product_ratings_page(request, id):
    product = get_object_or_404(Add_product, id=id)
    ratings = Rating.objects.filter(product=product).order_by('-created_at')

    return render(request, 'ratings_list.html', {
        'product': product,
        'ratings': ratings
    })
       
@login_required
def my_wishlist(request, id):
    product = get_object_or_404(Add_product, id=id)
    if product:
        Wishlist.objects.get_or_create(product=product, user=request.user)
        return redirect('wishlist_sucses')
    return render(request, 'wishlist.html', {'product': product})
@login_required
def wishlist_sucses(request):
    return render(request, 'w_sucses.html')
@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist_list.html', {
        'wishlist_items': wishlist_items
    })
from django.utils import timezone
from django.db.models import Sum

@login_required
def my_dashboard(request):
    pending = Book_product.objects.select_related('user').filter(status="pending").order_by('-created_at')
    confirmed = Book_product.objects.filter(status="confirmed").order_by('-created_at')
    cancelled = Book_product.objects.filter(status='cancelled').order_by('-created_at')
    all_orders = Book_product.objects.all().order_by('-created_at')
    most_wishlist = Wishlist.objects.all().order_by('-id')
    today = timezone.now().date()

    # Today's revenue
    daily_revenue = Book_product.objects.filter(
        status="confirmed",
        created_at__date=today
    ).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    # Current month's revenue
    monthly_revenue = Book_product.objects.filter(
        status="confirmed",
        created_at__year=today.year,
        created_at__month=today.month
    ).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    return render(request, 'dashboard.html', {
    'pending': pending,
    'confirmed': confirmed,
    'cancelled': cancelled,
    'all_orders': all_orders,
    'most_wishlist': most_wishlist,
    'daily_revenue': daily_revenue,
    'monthly_revenue': monthly_revenue
})
from django.db.models import Q

@login_required
def my_worklist(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    all_products = Book_product.objects.select_related(
        'user', 'product'
    ).order_by('-created_at')
    if search_query:
        all_products = all_products.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    # Apply status filter
    if status_filter in ['pending', 'confirmed', 'cancelled']:
        all_products = all_products.filter(status=status_filter)


    return render(request, 'worklist.html', {
        'all_products': all_products,
        'search_query': search_query,
        'status_filter': status_filter,
    })

    
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
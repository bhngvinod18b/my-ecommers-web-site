from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('user-home/', views.user_home, name='user_home'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('add-employe/', views.add_employe, name='add_employe'),
    path('manager-profile/', views.manager_profile, name='manager_profile'),
    path('add-product/', views.product_add, name='product_add'),
    path('customer/', views.customer, name='customer'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer-home/', views.customer_home, name='customer_home'),
    path('success/', views.succes_page, name='succes_page'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('update-status/<int:order_id>/', views.update_status, name='update_status'),
    path('delete-order/<int:id>/', views.delete_my_orders, name='delete_my_orders'),
    path('place-order/<int:id>/', views.place_order, name='place_order'),
    path('inbox/',views.inbox,name='inbox'),
    
]
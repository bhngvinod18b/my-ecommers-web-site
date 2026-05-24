from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50, default=1010)
    employe_id = models.CharField(max_length=50)
    department = models.CharField()
    phone = models.CharField(max_length=50)
    def __str__(self):
        return f'{'name'} by {'phone'}'
    
class Manager(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    def __str__(self):
        return f'{'name'} by {'phone'}'
    
class Add_product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_name')
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    catogery = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f'{self.user} added {self}'
    
class Book_product(models.Model):
    product = models.ForeignKey(Add_product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    STATUS_CHOICES =  (('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),)
    address = models.TextField(null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,
        default='pending'
    )
     # ✅ auto total price
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} booked {self.product}'

    class Meta:
        pass
class Customer_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    adress = models.CharField(max_length=100)
    gmail = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.name} is {self.phone}'

class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f'{'self.user'} is {'self.role'}'
from django.contrib import admin
from .models import Book_product

class BookProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('product__product', 'user__username')

admin.site.register(Book_product, BookProductAdmin)
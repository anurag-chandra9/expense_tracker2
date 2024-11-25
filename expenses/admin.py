from django.contrib import admin
from .models import Expense

# Register your models here.

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'date', 'created_at')
    list_filter = ('category', 'date')
    search_fields = ('title', 'category')
    ordering = ('-date',)

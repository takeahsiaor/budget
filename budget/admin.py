from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.db import models
from django import forms
from django.templatetags.static import static
from budget.models import (Transaction, Category, Budget, BudgetCategory,
        RecurringTransactionDef
    ) 

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'transaction_type')
    ordering = ('-date',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes')
    ordering = ('name',)

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('year', 'month')

class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'amount')

admin.site.register(RecurringTransactionDef)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(BudgetCategory, BudgetCategoryAdmin)

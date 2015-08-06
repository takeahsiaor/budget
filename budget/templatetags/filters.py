from django import template
from django.db.models import Sum

from budget.models import Transaction

register = template.Library()

# def parse_budgetcategory(budgetcategory):
#     '''
#     Takes in a BudgetCategory object and returns out the
#     sum expense and income for that month
#     '''
#     budget = budgetcategory.budget
#     category = budgetcategory.category
#     expenses = Transaction.objects.filter(budget=budget, category=category,
#             transaction_type='expense'
#         ).aggregate(Sum('amount'))
#     income = Transaction.objects.filter(budget=budget, category=category,
#             transaction_type='income'
#         ).aggregate(Sum('amount'))
#     expenses_val = 0 if not expenses['amount__sum'] else expenses['amount__sum']
#     income_val = 0 if not income['amount__sum'] else income['amount__sum']
#     return expenses_val, income_val

# @register.filter
# def amount_left_in_category(budgetcategory):
#     total = budgetcategory.amount
#     expenses, income = parse_budgetcategory(budgetcategory)
#     left = total + income - expenses
#     return left

# @register.filter
# def amount_spent_in_category(budgetcategory):
#     expenses, income = parse_budgetcategory(budgetcategory)
#     spent = expenses - income
#     return spent


# register.filter('amount_left_in_category', amount_left_in_category)
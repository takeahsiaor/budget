import datetime
import json

from django import forms
from django.contrib import messages
from django.db.models import Sum
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView, CreateView

from budget.forms import (BudgetForm, BudgetCategoryForm, TransactionForm,
        BudgetCategoryFormSet, RecurringTransactionForm, CategoryForm,
        Category
    )
from budget.models import (Transaction, Budget, BudgetCategory,
        RecurringTransactionDef
    )

def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    month = budget.month
    year = budget.year
    budget.delete()
    messages.success(
            request,
            'Budget for %s, %s successfully deleted' % (month, year)
        )
    return HttpResponseRedirect(reverse('budgets'))

def deactivate_recurring_transaction_def(request, pk):
    '''
    sets recurring transaction def to inactive. If we delete it, then the 
    transactions created will be deleted in the cascade.
    '''
    recurring_def = get_object_or_404(RecurringTransactionDef, pk=pk)
    recurring_def.active = False
    recurring_def.save()
    messages.success(
            request,
            "Recurring transaciton successfully deleted!"
        )
    return HttpResponseRedirect(reverse('recurring_transactions'))

def delete_transaction(request):
    transaction_id = request.POST.get('transaction_id')
    # import ipdb; ipdb.set_trace()
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    transaction_type = transaction.transaction_type
    amount = transaction.amount
    category = transaction.category
    transaction.delete()

    messages.success(request,
            'Successfully deleted %s transaction of $%s from %s' % (
                    transaction_type, amount, category
                )
        )
    return HttpResponse()

def update_transaction(request):
    transaction_id = request.POST.get('pk')
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    field = request.POST.get('name')
    value = request.POST.get('value')

    setattr(transaction, field, value)
    try:
        # transaction.clean()
        transaction.save()
        return HttpResponse('Success!')
    except:
        response_data = {'status': 'error', 'msg': 'Invalid Entry!'}
        response_json = json.dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')

def get_budget_summary(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    details = budget.get_details()
    del details['income_transactions']
    del details['expense_transactions']
    del details['budget_categories']
    response_json = json.dumps(details)
    return HttpResponse(response_json, content_type="application/json")

class OverviewView(TemplateView):
    template_name = 'overview.html'

    def get_context_data(self, *args, **kwargs):
        context = super(OverviewView, self).get_context_data(*args, **kwargs)
        budgets = Budget.objects.all()
        budget_contexts = []
        categories = Category.objects.all()
        date_data = []
        income_data = []
        expense_data = []
        net_income_data = []
        for budget in budgets:
            total_income = budget.get_total_income()
            total_expenses = budget.get_total_expenses()
            budget_contexts.append({
                    'total_income':total_income,
                    'total_expenses':total_expenses,
                    'net_income':total_income - total_expenses,
                    'three_month_net':budget.get_three_month_net_income(),
                    'year_net':budget.get_yearly_net_income(),
                    'start_date':budget.start_date,
                    'id':budget.id
                })
            date_data.append(budget.start_date.strftime('%b %y'))
            income_data.append(total_income)
            expense_data.append(total_expenses)
            net_income_data.append(round(total_income - total_expenses, 2))
        context.update({
            'budgets': budget_contexts,
            'categories': categories,
            'date_data': date_data,
            'income_data': income_data,
            'expense_data': expense_data,
            'net_income_data': net_income_data})
        return context

class CategoryOverview(TemplateView):
    template_name = 'category_overview.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryOverview, self).get_context_data(*args, **kwargs)
        category_id = kwargs.get('pk')
        if not category_id:
            raise Http404
        category = get_object_or_404(Category, id=category_id)

        # get all the expense budget categories and their context
        expense_budget_categories = BudgetCategory.objects.filter(
            category=category, income=False)
        expense_bc_contexts = []
        #expense_left_data = []
        expense_spent_data = []
        expense_date_data = []
        expense_budgeted_data = []
        for bc in expense_budget_categories:
            left = bc.amount_left_in_category()
            spent = bc.amount_spent_in_category()
            expense_bc_contexts.append({
                    'left': left,
                    'spent': spent,
                    'date': bc.budget.start_date,
                    'budgeted': bc.amount,
                    'id': bc.id,
                    'budget_id':bc.budget.id
                })
            expense_date_data.append(bc.budget.start_date.strftime('%b %y'))
            expense_spent_data.append(float(spent))
            #expense_left_data.append(float(left))
            expense_budgeted_data.append(float(bc.amount))

        #get the income budget categories and their context
        income_budget_categories = BudgetCategory.objects.filter(
            category=category, income=True)
        income_bc_contexts = []
        #income_left_data = []
        income_earned_data = []
        income_date_data = []
        income_budgeted_data = []
        for bc in income_budget_categories:
            left = bc.amount_left_in_category()
            earned = bc.amount_earned_in_category()
            income_bc_contexts.append({
                    'left': left,
                    'earned': earned,
                    'date': bc.budget.start_date,
                    'budgeted': bc.amount,
                    'id': bc.id,
                    'budget_id':bc.budget.id
                })
            income_date_data.append(bc.budget.start_date.strftime('%b %y'))
            income_earned_data.append(float(earned))
            #income_left_data.append(float(left))
            income_budgeted_data.append(float(bc.amount)) 

        context.update({
                'category':category,
                'expense_budget_categories':expense_bc_contexts,
                'expense_date_data':expense_date_data,
                'expense_spent_data':expense_spent_data,
                'expense_budgeted_data':expense_budgeted_data,
                'income_budget_categories':income_bc_contexts,
                'income_date_data':income_date_data,
                'income_earned_data':income_earned_data,
                'income_budgeted_data':income_budgeted_data,
            })
        return context

def get_transactions_for_budget_category(request):
    pk = request.GET.get('pk')
    if not pk:
        raise Http404
    bc = get_object_or_404(BudgetCategory, id=pk)
    transactions = Transaction.objects.filter(
        budget=bc.budget, category=bc.category)
    return render(request, 'transactions_for_bc.html',
        {'transactions':transactions, 'budget_category':bc})

def get_transactions_for_budget(request):
    pk = request.GET.get('pk')
    if not pk:
        raise Http404
    budget = get_object_or_404(Budget, id=pk)
    transactions = Transaction.objects.filter(
        budget=budget)
    return render(request, 'transactions_for_budget.html',
        {'transactions':transactions, 'budget':budget})

# Create your views here.
class BudgetCategoryFormView(TemplateView):
    template_name = 'edit_budget_category_form.html'
    BudgetCategoryFormSet = formset_factory(
            BudgetCategoryForm, formset=BudgetCategoryFormSet,
            can_delete=True, extra=2)

    def dispatch(self, *args, **kwargs):
        self.budget = get_object_or_404(Budget, pk=kwargs.get('pk'))
        return super(BudgetCategoryFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        budget_categories = BudgetCategory.objects.filter(
            budget=self.budget)

        #build initial data from existing models
        values_list = []
        for bc in budget_categories:
            values_list.append({'budget':bc.budget, 'amount':bc.amount, 
                'category':bc.category, 'income':bc.income})

        context = super(BudgetCategoryFormView, self).get_context_data(
            *args, **kwargs)
        category_formset = self.BudgetCategoryFormSet(initial=values_list)
        context.update({'category_formset':category_formset,
                'budget':self.budget}
            )
        return context

    def post(self, request, *args, **kwargs):
        category_formset = self.BudgetCategoryFormSet(request.POST)
        if category_formset.is_valid():
            for form in category_formset:
                if form.has_changed():

                    form.save(self.budget)

            messages.success(request, 
                    "You've updated this budget successfully"
                )
            return HttpResponseRedirect(
                    reverse('edit_categories', kwargs={'pk':kwargs.get('pk')})
                )
        return render(request, self.template_name, 
                {'category_formset':category_formset, 'budget':self.budget}
            )

class CreateBudgetFormView(CreateView):
    template_name = 'create_budget_form.html'
    # success_url = '/budgets/' #this should direct to budget categories form view
    model = Budget
    fields = ['month', 'year']

    def get_form(self, form_class):
        form = super(CreateBudgetFormView, self).get_form(form_class)
        form.fields['month'].widget.attrs.update({'class':'form-control'})
        form.fields['year'].widget.attrs.update({'class':'form-control'})
        return form

    def form_valid(self, form):
        #there must be a better place to put this
        #if there is a pk kwarg, this means that we want to create this budget
        #but clone the categories of the budget matching pk
        budget_to_clone_pk = self.kwargs.get('pk')
        bcs_to_clone = []
        if budget_to_clone_pk:
            budget_to_clone = Budget.objects.get(pk=budget_to_clone_pk)
            bcs_to_clone = BudgetCategory.objects.filter(
                budget=budget_to_clone)

        self.object = form.save()

        for bc in bcs_to_clone:
            new_bc = BudgetCategory(
                    budget=self.object,
                    category=bc.category,
                    amount=bc.amount,
                    income=bc.income
                )
            new_bc.save()
        if budget_to_clone_pk:
            messages.success(
                    self.request,
                    "You've successfully cloned the %s" % budget_to_clone
                )
        else:
            messages.success(self.request, "New budget created!")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        created_budget = self.object
        return reverse('edit_categories', kwargs={'pk':created_budget.pk})

class CategoryFormView(FormView):
    template_name = 'category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('category_types')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
            "You've successfully added a category type!")
        return super(CategoryFormView, self).form_valid(form)


class RecurringTransactionFormView(FormView):
    template_name = 'recurring_transaction_form.html'
    form_class = RecurringTransactionForm
    success_url = reverse_lazy('recurring_transactions') #really? look into lazyloading reverse

    def dispatch(self, request, *args, **kwargs):
        #figure out whether this is creating a new object or 
        #editing an existing one
        pk = kwargs.get('pk')
        if pk:
            recurring = RecurringTransactionDef.objects.filter(pk=pk)
            self.initial = recurring.values()[0]
            #values off object give category_id not category so need
            #to manually add in category key into initial.
            self.initial.update({'category':recurring[0].category})
        return super(RecurringTransactionFormView, self).dispatch(
                request, *args, **kwargs
            )

    def form_valid(self, form):
        pk = None
        if self.initial:
            pk = self.initial.get('id')
        form.save(pk=pk)
        if pk:
            messages.success(self.request,
                "You've successfully edited a recurring transaction!")
        else:
            messages.success(self.request,
                "You've successfully added a recurring transaction!")
        return super(RecurringTransactionFormView, self).form_valid(form)

#This formview is somewhat unncessary now since we have the form 
#in the budget detail view. deprecated
# class TransactionFormView(FormView):
#     template_name = 'transaction_form.html'
#     form_class = TransactionForm
#     success_url = '/transactions/'

#     def get_context_data(self, *args, **kwargs):
#         context = super(TransactionFormView, self).get_context_data(
#                 *args, **kwargs)
#         today = datetime.date.today()
#         month = today.month
#         year = today.year
#         budget, created = Budget.objects.get_or_create(month=month, year=year)

#         context.update({
#                 'summary':budget.get_details()
#             })
#         return context

#     def form_valid(self, form):        
#         obj = form.save()
#         messages.success(self.request,
#             "You've successfully added a transaction to %s!" % obj.budget)
#         return super(TransactionFormView, self).form_valid(form)

class RecurringTransactionListView(ListView):
    model = RecurringTransactionDef
    template_name = 'recurring_transactions_list.html'
    queryset = RecurringTransactionDef.objects.filter()
    context_object_name = 'recurring_transactions'

class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    queryset = Category.objects.all().order_by('name')
    context_object_name = 'category_list'

class BudgetListView(ListView):
    model = Budget
    template_name = 'budget_list.html'
    queryset = Budget.objects.all().order_by('-year', '-month')
    context_object_name = 'budget_list'

    #paginate this later
    # def get_context_data(self, *args, **kwargs):
    #     context = super(BudgetListView, self).get_context_data(*args, **kwargs)
    #     budget_list = s

def current_budget(request):
    today = datetime.datetime.today()
    month = today.month
    year = today.year

    budget = get_object_or_404(Budget, month=month, year=year)
    return redirect(reverse_lazy('budget', kwargs={'pk':budget.pk}))

class BudgetView(DetailView):
    model = Budget
    template_name = 'budget_detail.html'
    context_object_name = 'budget'

    def get_context_data(self, *args, **kwargs):
        context = super(BudgetView, self).get_context_data(*args, **kwargs)
        budget = self.object
        today = datetime.datetime.today()
        this_month = today.month
        this_year = today.year

        #if looking at the current month, give today's date otherwise the first
        #of the month

        #mimic last transaction inputted into given budget

        last_transactions = Transaction.objects.filter(
                budget=budget, recurring_transaction_def__isnull=True
            ).order_by('-pk')
        if last_transactions:
            last = last_transactions[0]
            transaction_form = TransactionForm(
                initial={'date': last.date, 'category': last.category,
                    'transaction_type': last.transaction_type})
            
        elif this_month == budget.month and this_year == budget.year:
            transaction_form = TransactionForm(
                    initial={'date':today.date()})
        else:
            transaction_form = TransactionForm(
                    initial={'date':budget.start_date})

        context.update({
                'summary': budget.get_details(),
                'transaction_form': transaction_form 
            })
        return context


    def post(self, request, *args, **kwargs):
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction_form.save()
            #at this point in the method call chain, self.object does not exist
            #so use self.get_object() instead
            messages.success(request,
                "You've succesfully added a tranaction to %s!" % \
                self.get_object())
            return super(BudgetView, self).get(request, *args, **kwargs)

        context = self.get_context_data(*args, **kwargs)
        context.update({'transaction_form': transaction_form})
        return render(request, self.template_name, context)

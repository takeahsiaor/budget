import datetime

from django import forms
from django.forms.formsets import BaseFormSet

from recurrence.forms import RecurrenceWidget

from budget.models import (Transaction, Budget, BudgetCategory, MONTHS,
        RecurringTransactionDef, Category
    )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        widgets = {
                'name': forms.TextInput(attrs={'class':'form-control'}),
                'notes': forms.TextInput(attrs={'class':'form-control'})
            }

class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransactionDef
        fields = [
                'start_date', 'category', 'amount', 'transaction_type',
                'recurrences','notes', 'active'   
            ]
        widgets = {
                'start_date': forms.DateInput(attrs={'class':'form-control'}),
                'category': forms.Select(attrs={'class':'form-control'}),
                'amount': forms.NumberInput(attrs={
                    'class':'form-control',
                    'placeholder':'$0.00'}),
                'notes': forms.TextInput(attrs={
                    'class':'form-control', 
                    'placeholder':'Enter details of transaction'}),
                'recurrences': RecurrenceWidget(),
                'transaction_type': forms.Select(attrs={'class':'form-control'}),
            }
    def save(self, pk=None):
        if pk:
            rt = RecurringTransactionDef.objects.filter(pk=pk)
            cd = self.cleaned_data
            rt.update(start_date=cd['start_date'], category=cd['category'],
                    amount=cd['amount'], notes=cd['notes'],
                    transaction_type=cd['transaction_type'],
                    recurrences=cd['recurrences'], active=cd['active']
                )
        else:
            return super(RecurringTransactionForm, self).save()
    

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'category',
            'amount', 'notes', 'for_business']

        widgets = {
                'date': forms.DateInput(attrs={'class':'form-control'}),
                'transaction_type': forms.Select(attrs={'class':'form-control'}),
                'category': forms.Select(attrs={'class':'form-control'}),
                'amount': forms.NumberInput(attrs={
                    'class':'form-control',
                    'placeholder':'$0.00'}),
                'notes': forms.TextInput(attrs={
                    'class':'form-control', 
                    'placeholder':'Enter details of transaction'}),
                'for_business': forms.CheckboxInput()
            }

        labels = {
            'for_business': 'Business related transaction?'
        }

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(status=True)

    def save(self):
        '''
        manually sets the budget this is associated with based on the 
        input date
        '''
        cd = self.cleaned_data
        date = cd['date']
        month = date.month
        year = date.year
        budget, created = Budget.objects.get_or_create(month=month, year=year)
        transaction = Transaction(date=date, transaction_type=cd['transaction_type'],
            category=cd['category'], amount=cd['amount'], notes=cd['notes'],
            budget=budget, for_business=cd['for_business'])
        transaction.save()
        return transaction


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['month', 'year']

        widgets = {
                'month': forms.Select(attrs={'class':'form-control'}),
                'year': forms.TextInput(attrs={'class':'form-control',
                    'placeholder':'20XX'})
            }
    # month = forms.ChoiceField(choices=MONTHS, required=True)
    # year = froms.IntegerField(max_length=4, required=True)

class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        exclude = ['budget']
        fields = ['category', 'amount', 'income']
        widgets = {
                'category': forms.Select(attrs={'class':'form-control'}),
                'amount': forms.NumberInput(attrs={
                    'class':'form-control',
                    'placeholder':'$0.00'}),
                'income': forms.CheckboxInput(),
            }

    def __init__(self, *args, **kwargs):
        super(BudgetCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(status=True)

    def save(self, budget):
        category = self.cleaned_data['category']
        amount = self.cleaned_data['amount']
        income = self.cleaned_data['income']
        #Use a get on cleaned_data in case not used with a formset with
        #can_delete = False
        delete = self.cleaned_data.get('DELETE')
        if delete:
            #Delete the object if the delete checkbox is checked
            #Use a filter in case they put a delete next to an uninitialized
            #form and the BudgetCategory doesn't yet exist
            BudgetCategory.objects.filter(
                    budget=budget, category=category
                ).delete()
            return

        budget_category, created = BudgetCategory.objects.update_or_create(
                budget=budget, category=category, income=income,
                defaults={'amount':amount}
            )

class BudgetCategoryFormSet(BaseFormSet):
    """
    Custom formset to ensure that a budget's categories must be unique
    """    
    def clean(self):
        categories = []
        for form in self.forms:
            if not form.has_changed():
                continue
            category = form.cleaned_data['category']
            if category in categories:
                raise forms.ValidationError(
                        "You can't have more than one of the same category in a budget!"
                    )
            categories.append(category)


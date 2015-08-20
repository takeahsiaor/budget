import calendar
import datetime
from django.db import models
from django.db.models import Sum, Q

from recurrence.fields import RecurrenceField

TRANSACTION_TYPES = [('income', 'Income'), ('expense', 'Expense')]

MONTHS = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)


class RecurringTransactionDef(models.Model):
    '''
    RecurringTransactionDef represents the "template" by which transactions
    are generated on a recurring basis.

    The transactions themselves are Transaction objects with foreign key to 
    this def.
    '''
    TIME_INTERVALS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ]
    category = models.ForeignKey('Category')
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    transaction_type = models.CharField(choices=TRANSACTION_TYPES,
        default='expense', max_length=7)
    notes = models.CharField(max_length=1023, blank=True, null=True)
    recurrences = RecurrenceField(blank=True, null=True)

    last_update = models.DateField(auto_now=True)

    #indicates the date user wants recurring transactions to start
    #start_date cannot be in the past - to be enforced in form?
    start_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def get_recurrences_between(self, start_date, end_date):
        '''input: date objects, output=list of dates that transactions 
        will be made'''
        #bad hack here:
        #between function does gt instead of gte
        start_date = start_date - datetime.timedelta(days=1)
        start_date = datetime.datetime.combine(
                start_date, datetime.datetime.max.time()
            )
        end_date = datetime.datetime.combine(
                end_date, datetime.datetime.max.time()
            )
        transaction_datetimes = self.recurrences.between(
                start_date, end_date, dtstart=start_date
            )
        transaction_dates = [dt.date() for dt in transaction_datetimes]
        return transaction_dates

    def pending_budgets(self):
        '''
        This will return a list of budgets that have not yet had this
        def create a transaction for this.
        '''

        in_range = Budget.objects.filter(start_date__gte=self.start_date)
        pending = []
        for budget in in_range:
            transaction_dates = self.get_recurrences_between(
                budget.start_date, budget.end_date)

            for transaction_date in transaction_dates:
                #check for each date whether or not the transaction exists
                recurring_transaction = Transaction.objects.filter(
                        recurring_transaction_def=self, budget=budget,
                        date=transaction_date
                    )
                if not recurring_transaction:
                    pending.append(budget)
                    break
        return pending

    def create_transactions(self, budget=None):
        '''
        This will create the transactions for all existing budgets that
        satisfy the recurring interval and ordinal.

        If a budget is passed in, this will only create the transaction for
        given budget.

        This contains the logic of the actual creation and assignment
        '''
        if not self.active:
            return

        if budget:
            budgets = [budget]
        else:
            budgets = self.pending_budgets()

        for budget in budgets:
            transaction_dates = self.get_recurrences_between(
                budget.start_date, budget.end_date)

            for transaction_date in transaction_dates:
                transaction, created = Transaction.objects.get_or_create(
                        date=transaction_date, 
                        transaction_type=self.transaction_type,
                        category=self.category, budget=budget,
                        amount=self.amount, notes=self.notes,
                        recurring_transaction_def=self)
                if created: print 'created transaction for %s' % transaction

    def save(self):
        #how shoudl i handle editing recurring? edit for all or just future?
        super(RecurringTransactionDef, self).save()
        self.create_transactions()

    def __unicode__(self):
        return "Recurring payment of %s for %s" % (
                self.amount, self.category
            )

class RecurringTransactionManager(models.Manager):
    def create_transactions(self):
        '''
        This is meant to be called when a budget is created for the first time.
        Or when a RecurringTransactionDef is created.

        Actually creates the individual transactions from the 
        RecurringTransactionDef.


        This handles the filtering of which RecurringTransactionDefs should
        call the object method create_transactions
        '''
        actives = RecurringTransactionDef.objects.filter(active=True)
        for active in actives:
            active.create_transactions(budget)

    
class TransactionManager(models.Manager):
    def income_transactions(self, month, year):
        #should factor out this kind of "find month" pattern
        start_date = datetime.datetime(month=month, year=year, day=1)
        end_date = start_date.replace(month=month+1)
        transactions = Transaction.objects.filter(
                date__gte=start_date, date__lt=end_date,
                transaction_type='income'
            )
        return transactions

    def expense_transactions(self, month, year):
        #should factor out this kind of "find month" pattern
        start_date = datetime.datetime(month=month, year=year, day=1)
        end_date = start_date.replace(month=month+1)
        transactions = Transaction.objects.filter(
                date__gte=start_date, date__lt=end_date,
                transaction_type='expense'
            )
        return transactions

class Transaction(models.Model):
    objects = TransactionManager()

    date = models.DateField()
    transaction_type = models.CharField(choices=TRANSACTION_TYPES,
        default='expense', max_length=7)
    category = models.ForeignKey('Category')
    budget = models.ForeignKey('Budget')
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    notes = models.CharField(max_length=1023, blank=True, null=True)

    recurring_transaction_def = models.ForeignKey(
            RecurringTransactionDef, blank=True, null=True
        )

    # def clean(self):
    #     try:
    #         if '$' in self.amount:
    #             self.amount = self.amount.replace('$', '')
    #         return super(Transaction, self).clean()
    #     except:
    #         return super(Transaction, self).clean()

    def __unicode__(self):
        return '%s %s in %s in %s' % (
                self.amount, self.transaction_type, self.category, self.budget
            )

class Category(models.Model):

    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=255)
    notes = models.CharField(max_length=1023, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Budget(models.Model):

    class Meta:
        unique_together = ('month', 'year')

    month = models.IntegerField(choices=MONTHS)
    year = models.IntegerField(
        help_text="Enter full year not just 15")

    #the start date will be extrapolated from the month and year
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    categories = models.ManyToManyField(
            'Category', through='BudgetCategory', blank=True, null=True
        )

    #should this really be in budget? this is gathered from BudgetCategories
    #i guess this could be used if you want this to be the max and
    #you use percetnages to determine category amounts
    projected_spent = models.DecimalField(
            decimal_places=2, blank=True, null=True, max_digits=15
        )

    #does this need to exist? shouldn't it just be a category?
    projected_earned = models.DecimalField(
            decimal_places=2, blank=True, null=True, max_digits=15
        )

    #can implement percentage based amounts in categories later in lieu of
    #dollar amounts in BudgetCategory
    def month_and_year(self):
        return self.month, self.year

    def get_income_transactions(self):
        month, year = self.month_and_year()
        income = Transaction.objects.income_transactions(month, year)
        return income

    def get_total_income(self):
        income = self.get_income_transactions()
        total_income = income.aggregate(Sum('amount'))['amount__sum']
        if not total_income: total_income = 0
        return float(total_income)

    def get_expense_transactions(self):
        month, year = self.month_and_year()
        expenses = Transaction.objects.expense_transactions(month, year)
        return expenses

    def get_total_expenses(self):
        expenses = self.get_expense_transactions()
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
        if not total_expenses: total_expenses = 0
        return float(total_expenses)

    def get_net_income(self):
        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()
        net_income = total_income - total_expenses
        return float(net_income)

    def get_net_expense_for_category(self, category):
        """accepts category object and returns the total expense for that
        category in this budget"""
        all_income = self.get_income_transactions()
        category_income = all_income.filter(category=category).aggregate(
                Sum('amount'))['amount__sum']
        if not category_income: category_income = 0

        all_expenses = self.get_expense_transactions()
        category_expense = all_expenses.filter(category=category).aggregate(
                Sum('amount'))['amount__sum']
        if not category_expense: category_expense = 0

        return category_expense - category_income


    def get_worst_category(self):
        """
        currently worst is defined as having the spent the most relative to
        the budget allotted to it.

        measured by percent saved
        """
        budget_categories = BudgetCategory.objects.filter(budget=self)
        worst_category_percent = 100
        worst_category = None
        worst_category_name = "None"
        percent_display = 'N/A'
        for bc in budget_categories:
            category = bc.category
            net_expense = self.get_net_expense_for_category(category)
            budgeted = bc.amount
            category_percent_saved = (budgeted - net_expense)/budgeted * 100
            if category_percent_saved < worst_category_percent:
                worst_category_percent = category_percent_saved
                worst_category = category
        #if i'm rounding anyways, no point in giving decimal
        worst_category_percent = int(round(worst_category_percent))
        if worst_category:
            worst_category_name = worst_category.name
            percent_display = worst_category_percent
        return (worst_category_name, percent_display)

    def get_best_category(self):
        budget_categories = BudgetCategory.objects.filter(budget=self)
        best_category_percent = -1000
        best_category = None
        best_category_name = "None"
        percent_display = 'N/A'
        for bc in budget_categories:
            category = bc.category
            net_expense = self.get_net_expense_for_category(category)
            budgeted = bc.amount
            category_percent_saved = (budgeted - net_expense)/budgeted * 100
            if category_percent_saved > best_category_percent:
                best_category_percent = category_percent_saved
                best_category = category
        best_category_percent = int(round(best_category_percent))

        if best_category:
            best_category_name = best_category.name
            percent_display = best_category_percent
        return (best_category_name, percent_display)

    def get_three_month_net_income(self):
        month_1 = self.start_date
        month_2 = (month_1 - datetime.timedelta(days=1)).replace(day=1)
        month_3 = (month_2 - datetime.timedelta(days=1)).replace(day=1)

        primary_budget_net = self.get_net_income()

        secondary_budget = Budget.objects.filter(
                month=month_2.month, year=month_2.year)
        if secondary_budget:
            secondary_budget_net = secondary_budget[0].get_net_income()
        else:
            secondary_budget_net = 0

        tertiary_budget = Budget.objects.filter(
                month=month_3.month, year=month_3.year)
        if tertiary_budget:
            tertiary_budget_net = tertiary_budget[0].get_net_income()
        else:
            tertiary_budget_net = 0

        return float(
            primary_budget_net + secondary_budget_net + tertiary_budget_net)

    def get_details(self):
        """
        wrapper function to get a bunch of information already exposed by 
        different methods that will commonly be needed together. really for 
        convenience

        returns income transactions queryset, expense transactions queryset,
        budget categories, total income, total expenses, net income,
        net income three months,
        as a dict
        """
        income = self.get_income_transactions()
        expenses = self.get_expense_transactions()

        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()

        net_income = self.get_net_income()
        three_month_net = self.get_three_month_net_income()
        budget_categories = BudgetCategory.objects.filter(budget=self)

        worst_category, worst_category_save_percent = self.get_worst_category()
        best_category, best_category_save_percent = self.get_best_category()

        return {'income_transactions':income, 'expense_transactions':expenses,
            'total_income':total_income, 'total_expenses':total_expenses,
            'net_income':net_income, 'budget_categories':budget_categories,
            'three_month_net':three_month_net, 'worst_category':worst_category,
            'worst_category_save_percent':worst_category_save_percent,
            'best_category_save_percent':best_category_save_percent,
            'best_category':best_category,

        }

    def save(self, **kwargs):
        self.start_date = datetime.datetime(
                month=self.month, day=1, year=self.year)
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        self.end_date = datetime.datetime(month=self.month, day=days_in_month,
                year=self.year)

        #distinguish whether editing or creating.
        if not self.id:
            super(Budget, self).save(**kwargs)
            #look for all recurring transaction definitions that
            #will apply to this newly created budget
            recurring_defs = RecurringTransactionDef.objects.filter(
                    active=True, start_date__lte=self.start_date
                )
            for recurring_def in recurring_defs:
                recurring_def.create_transactions(self)
            return

        super(Budget, self).save(**kwargs)

    def __unicode__(self):
        return 'Budget for %s, %s' % (self.month, self.year)

class BudgetCategory(models.Model):
    '''This represents the relation between an individual month's budget
    and the category type.

    This is where we put the amount allocated to a particular category for 
    a given month'''

    class Meta:
        verbose_name_plural = "Budget Categories"
        unique_together = ('budget', 'category')

    budget = models.ForeignKey('Budget')
    category = models.ForeignKey('Category')
    amount = models.DecimalField(decimal_places=2, max_digits=15)

    def parse_budget_category(self):
        '''
        Returns the sum expense and income for its month
        '''
        budget = self.budget
        category = self.category
        expenses = Transaction.objects.filter(budget=budget, category=category,
                transaction_type='expense'
            ).aggregate(Sum('amount'))
        income = Transaction.objects.filter(budget=budget, category=category,
                transaction_type='income'
            ).aggregate(Sum('amount'))
        expenses_val = 0 if not expenses['amount__sum'] else expenses['amount__sum']
        income_val = 0 if not income['amount__sum'] else income['amount__sum']
        return expenses_val, income_val

    def amount_left_in_category(self):
        total = self.amount
        expenses, income = self.parse_budget_category()
        left = total + income - expenses
        return left

    def amount_spent_in_category(self):
        expenses, income = self.parse_budget_category()
        spent = expenses - income
        return spent

    def __unicode__(self):
        return '%s for %s' % (self.category, self.budget)


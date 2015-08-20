import datetime
from recurrence import Recurrence, Rule, Weekday
from django.test import TestCase
from budget.models import (BudgetCategory, Budget, Category, Transaction,
        RecurringTransactionDef)
from django.db.models import Sum



def make_transaction(budget, category, amount,
        transaction_type='expense', date=None):
    #helper function to create non recurring transaction
    if not date:
        date = datetime.date(year=2015, month=1, day=1)

    Transaction.objects.create(
            date=date, budget=budget, category=category, amount=amount,
            transaction_type=transaction_type)

class BaseBudgetTestCase(TestCase):
    def setUp(self):
        self.budget = Budget.objects.create(month=1, year=2015)
        self.category_misc = Category.objects.create(name='misc')
        self.budget_category_misc = BudgetCategory.objects.create(
                budget=self.budget, category=self.category_misc,
                amount=100
            )

        self.category_food = Category.objects.create(name='food')
        self.budget_category_food = BudgetCategory.objects.create(
                budget=self.budget, category=self.category_food,
                amount=100
            )
        make_transaction(self.budget, self.category_misc, 30, 'expense')
        make_transaction(self.budget, self.category_misc, 20, 'expense')
        make_transaction(self.budget, self.category_misc, 5, 'income')
        make_transaction(self.budget, self.category_misc, 10, 'income')

        make_transaction(self.budget, self.category_food, 100, 'expense')
        make_transaction(self.budget, self.category_food, 10, 'income')

        #make more than one category with transactions in them

class BudgetTestCase(BaseBudgetTestCase):

    def test_month_and_year(self):
        self.assertEqual(self.budget.month_and_year(), (1, 2015))

    def test_get_income_transactions(self):
        #how to check that querysets are virtually the same?
        income_amount1 = Transaction.objects.filter(
                budget=self.budget, 
                transaction_type='income'
            ).aggregate(Sum('amount'))['amount__sum']
        income_amount2 = self.budget.get_income_transactions().aggregate(
                Sum('amount'))['amount__sum']
        self.assertEqual(income_amount1, income_amount2)

    def test_get_total_income(self):
        self.assertEqual(self.budget.get_total_income(), 25)

    def test_get_total_expenses(self):
        self.assertEqual(self.budget.get_total_expenses(), 150)

    def test_get_net_income(self):
        self.assertEqual(self.budget.get_net_income(), -125)

    def test_get_net_income_for_category(self):
        self.assertEqual(
            self.budget.get_net_expense_for_category(self.category_misc), 35)
        self.assertEqual(
            self.budget.get_net_expense_for_category(self.category_food), 90)

    def test_get_worst_category(self):
        self.assertEqual(self.budget.get_worst_category(), ('food', 10))

    def test_get_best_category(self):
        self.assertEqual(self.budget.get_best_category(), ('misc', 65))


class BudgetCategoryTestCase(BaseBudgetTestCase):

    def test_parse_budget_category(self):
        #test that parse_budget_category method returns summation of
        #expenses and incomes correctly
        self.assertEqual(
            self.budget_category_misc.parse_budget_category(), (50, 15))

    def test_amount_left_and_spent(self):
        #test amount_left and spent in category methods
        self.assertEqual(self.budget_category_misc.amount, 100)
        self.assertEqual(
            self.budget_category_misc.amount_left_in_category(), 65)
        self.assertEqual(
            self.budget_category_misc.amount_spent_in_category(), 35)


class RecurringTransactionTestCase(BaseBudgetTestCase):

    def setUp(self):
        super(RecurringTransactionTestCase, self).setUp()
        #'monthly, on the 1st without end
        rule = Rule(bymonthday=[1], freq=1, interval=1)
        recurrence = Recurrence(rrules=[rule,])
        self.rtd1 = RecurringTransactionDef(
                category=self.category_misc,
                amount=150,
                transaction_type='expense',
                notes='here are some notes',
                recurrences=recurrence,
                start_date=datetime.date(year=2014, month=1, day=1)
            )
        #don't save the rtd since this will create the transactions
        friday = Weekday(4)
        rule2 = Rule(byday=[friday,], freq=2, interval=2)
        recurrence2 = Recurrence(rrules=[rule2,])
        self.rtd2 = RecurringTransactionDef(
                category=self.category_food,
                amount=100,
                transaction_type='expense',
                notes='food notes',
                recurrences=recurrence2,
                start_date=datetime.date(year=2014, month=1, day=1)
            )
        #make another rtd with multiple recurrences in a given month
        #make one for the last day of the month

    def test_get_recurrences_between(self):
        self.assertEqual(
            len(self.rtd1.get_recurrences_between(
                    self.budget.start_date, self.budget.end_date)),1 )

        self.assertEqual(
            len(self.rtd2.get_recurrences_between(
                    self.budget.start_date, self.budget.end_date)), 3)

    def test_pending_budgets(self):
        self.assertEqual(self.rtd1.pending_budgets(), [self.budget])
        self.assertEqual(self.rtd2.pending_budgets(), [self.budget])

    # def test_create_transactions_active(self):
    #     #make sure there aren't any first
    #     num_transactions_rtd1 = Transaction.objects.filter(
    #         budget=self.budget, recurring_transaction_def=self.rtd1).count()
    #     num_transactions_rtd2 = Transaction.objects.filter(
    #         budget=self.budget, recurring_transaction_def=self.rtd2).count()
    #     self.assertEqual(num_transactions_rtd1, 0)
    #     self.assertEqual(num_transactions_rtd2, 0)

    #     self.rtd1.create_transactions()
    #     self.rtd2.create_transactions()
    #     transactions_rtd1 = Transaction.objects.filter(
    #         budget=self.budget, recurring_transaction_def=self.rtd1)
    #     transactions_rtd2 = Transaction.objects.filter(
    #         budget=self.budget, recurring_transaction_def=self.rtd2)

    #     for trans in transactions_rtd1:
    #         self.assertEqual(trans.notes, 'here are some notes')
    #         self.assertEqual(trans.amount, 150)
    #         self.assertEqual(trans.transaction_type, 'expense')
    #         self.assertEqual(trans.category, self.category_misc)

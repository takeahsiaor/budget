from django.conf.urls import patterns, include, url
from django.conf import settings
import views

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('recurrence',),
}

urlpatterns = patterns('',
    # Examples:
    # url(r'^admin/$', include(admin.site.urls)),
    # url(r'^transactions/$', views.TransactionFormView.as_view(), 
    #     name='transactions'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^transactions/recurring/add/$',
        views.RecurringTransactionFormView.as_view(), name='add_recurring_transaction'),
    url(r'^transactions/recurring/(?P<pk>\d{1,8})/delete/$', 
        views.deactivate_recurring_transaction_def, name='deactivate_recurring_transaction'),
    
    url(r'^transactions/recurring/(?P<pk>\d{1,8})/edit/$',
        views.RecurringTransactionFormView.as_view(), name='edit_recurring_transaction'),
    
    url(r'^transactions/recurring/$', views.RecurringTransactionListView.as_view(),
        name='recurring_transactions'),
    url(r'^transactions/delete/$', views.delete_transaction,
        name="delete_transaction"),
    url(r'^transactions/update/$', views.update_transaction, name="update_transaction"),
    url(r'^budgets/$', views.BudgetListView.as_view(), name='budgets'),
    url(r'^budgets/(?P<pk>\d{1,8})/$', views.BudgetView.as_view(),
        name='budget'),
    url(r'^budgets/new/$', views.CreateBudgetFormView.as_view(), name='create_budget'),
    url(r'^budgets/(?P<pk>\d{1,8})/edit-categories/$',
        views.BudgetCategoryFormView.as_view(), name='edit_categories'),
    url(r'^budgets/(?P<pk>\d{1,8})/clone/$',
        views.CreateBudgetFormView.as_view(), name='clone_budget'),
    url(r'^budgets/(?P<pk>\d{1,8})/delete/$',
        views.delete_budget, name='delete_budget'),
    url(r'^budgets/(?P<pk>\d{1,8})/get-summary/$', views.get_budget_summary,
        name='budget_summary'),
    url(r'^categories/$', views.CategoryListView.as_view(),
        name='category_types'),
    url(r'^categories/add/$', views.CategoryFormView.as_view(),
        name='create_category'),
    url(r'^overview/$', views.OverviewView.as_view(), name='overview'),
    url(r'^category-overview/(?P<pk>\d{1,8})/$', 
        views.CategoryOverview.as_view(), name='category_overview'),
    url(r'^transactions-in-budget-category/$',
        views.get_transactions_for_budget_category, name='get_transactions_for_budget_category'),



)
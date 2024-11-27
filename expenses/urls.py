from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('public/', views.public_dashboard, name='public_dashboard'),
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('add-expense/', views.add_expense_page, name='add_expense'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/profile/'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
    # API endpoints
    path('api/expenses/add/', views.add_expense, name='api_add_expense'),
    path('api/expenses/chart/', views.get_chart_data, name='api_chart_data'),
    path('api/expenses/total/', views.get_total_expenses, name='api_total_expenses'),
    path('api/expenses/recent/', views.get_recent_expenses, name='api_recent_expenses'),
]

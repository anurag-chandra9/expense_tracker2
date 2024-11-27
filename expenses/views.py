from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
import json
from .models import Expense
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .cache_utils import cached_view, cache_result, invalidate_cache_prefix

@login_required
@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

@login_required
@cached_view(timeout=300)  # Cache for 5 minutes
def expenses_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(expenses, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'expenses/list.html', {'page_obj': page_obj})

@login_required
def add_expense_page(request):
    return render(request, 'expenses/add.html')

@login_required
@require_http_methods(["POST"])
def add_expense(request):
    try:
        data = json.loads(request.body)
        expense = Expense.objects.create(
            user=request.user,
            title=data['title'],
            amount=data['amount'],
            date=data['date'],
            category=data['category']
        )
        # Invalidate relevant caches
        invalidate_cache_prefix(f"view:expenses_list")
        invalidate_cache_prefix(f"view:get_chart_data")
        invalidate_cache_prefix(f"view:get_recent_expenses")
        invalidate_cache_prefix(f"view:get_total_expenses")
        return JsonResponse({'success': True, 'id': expense.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@cached_view(timeout=300)  # Cache for 5 minutes
def get_chart_data(request):
    period = request.GET.get('period', 'month')
    today = datetime.now()
    
    if period == 'month':
        # Get data for current month, day by day
        start_date = today.replace(day=1)
        expenses = Expense.objects.filter(
            user=request.user,
            date__year=today.year,
            date__month=today.month
        ).order_by('date')
        
        # Create day labels
        days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day
        labels = [str(i) for i in range(1, days_in_month + 1)]
        values = [0] * days_in_month
        
        for expense in expenses:
            values[expense.date.day - 1] += float(expense.amount)
            
    else:  # year
        # Get data for current year, month by month
        expenses = Expense.objects.filter(
            user=request.user,
            date__year=today.year
        ).annotate(month=TruncMonth('date')).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Create month labels
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        values = [0] * 12
        
        for expense in expenses:
            month_idx = expense['month'].month - 1
            values[month_idx] = float(expense['total'])
    
    # Get category breakdown
    category_data = Expense.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    categories = [item['category'] for item in category_data]
    category_values = [float(item['total']) for item in category_data]
    
    return JsonResponse({
        'labels': labels,
        'values': values,
        'categories': categories,
        'category_values': category_values
    })

@login_required
@cached_view(timeout=300)  # Cache for 5 minutes
def get_recent_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    data = []
    for expense in expenses:
        data.append({
            'id': expense.id,
            'title': expense.title,
            'amount': float(expense.amount),
            'date': expense.date.strftime('%Y-%m-%d'),
            'category': expense.category
        })
    return JsonResponse(data, safe=False)

@login_required
@cached_view(timeout=300)  # Cache for 5 minutes
def get_total_expenses(request):
    try:
        total = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
        return JsonResponse({'total': float(total)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def profile_view(request):
    total_expenses = Expense.objects.filter(user=request.user).count()
    total_amount = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'total_expenses': total_expenses,
        'total_amount': total_amount,
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    return render(request, 'registration/edit_profile.html', {
        'user': request.user
    })

class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        try:
            user = form.get_user()
            if user.is_staff and not self.request.path.startswith('/admin/'):
                form.add_error(None, "Staff accounts must use the admin login page.")
                return self.form_invalid(form)
            auth_login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.username}!")
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, "An error occurred during login. Please try again.")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        for field in form.errors:
            for error in form.errors[field]:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

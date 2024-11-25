import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.contrib.auth.models import User

# Delete existing superuser if exists
User.objects.filter(username='admin').delete()

# Create new superuser
superuser = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)

print('Superuser created successfully!')

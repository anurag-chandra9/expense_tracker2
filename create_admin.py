import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.contrib.auth.models import User

# Remove all existing superusers
User.objects.filter(is_superuser=True).delete()

# Create a new superuser with simple credentials
User.objects.create_superuser(
    username='test',
    email='test@test.com',
    password='test'
)

print("Superuser created successfully!")
print("Username: test")
print("Password: test")

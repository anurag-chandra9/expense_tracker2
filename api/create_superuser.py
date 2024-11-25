from http.server import BaseHTTPRequestHandler
import os
import sys
import django
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        User = get_user_model()
        
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123')
            message = "Superuser created successfully!"
        else:
            message = "Superuser already exists!"

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())
        return

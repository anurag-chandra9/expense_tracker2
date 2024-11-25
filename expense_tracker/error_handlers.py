import sys
import traceback
from django.http import JsonResponse
from django.views.debug import ExceptionReporter
from django.conf import settings

def handler500(request):
    """Custom 500 error handler that logs error details."""
    type_, value, tb = sys.exc_info()
    
    # Get the full traceback
    reporter = ExceptionReporter(request, type_, value, tb)
    
    # Log the error (this will appear in Vercel logs)
    print('ERROR:', value)
    print('TRACEBACK:')
    print(reporter.get_traceback_text())
    
    return JsonResponse({
        'error': str(value),
        'type': str(type_.__name__),
        'detail': traceback.format_exc() if settings.DEBUG else 'Internal Server Error'
    }, status=500)

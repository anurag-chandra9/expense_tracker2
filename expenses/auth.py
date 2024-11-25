from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        try:
            # Check if username exists
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                raise ValidationError("Invalid username or password.")
            
            # Check password
            if not user.check_password(password):
                raise ValidationError("Invalid username or password.")
            
            # Check if user is active
            if not user.is_active:
                raise ValidationError("This account is inactive.")
            
            return user
            
        except ValidationError as e:
            # Re-raise validation errors to be caught by the form
            raise
        except Exception as e:
            # Log any unexpected errors
            print(f"Authentication error: {str(e)}")
            raise ValidationError("An error occurred during authentication.")

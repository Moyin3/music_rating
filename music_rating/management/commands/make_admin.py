from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class Command(BaseCommand):
    help = 'Make a user an admin (only if you are an admin)'

    def add_arguments(self, parser):
        # Add a positional argument for the username
        parser.add_argument('username', type=str)

    def handle(self, *args, **kwargs):
        # Get the current user who is executing the command (this could be passed as an argument or set manually)
        current_user = User.objects.get(username='current_admin')  # This should be the user running the command
        
        if not current_user.is_staff:
            raise PermissionDenied("You must be an admin to run this command.")

        # Proceed with the rest of the logic to make another user an admin
        username = kwargs['username']
        try:
            # Get the user by username
            user = User.objects.get(username=username)
            
            # Make the user an admin
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f"User {username} is now an admin."))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User {username} does not exist."))
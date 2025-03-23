from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

#TODO: Edit this script down the line if we have more people and I need someone that isn't me to make people admins while ensuring proper security.

class Command(BaseCommand):
    help = 'Makes a user an admin by their username.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user you want to promote to admin')
        parser.add_argument('current_user', type=str, help='The username of the user running this command')

    def handle(self, *args, **options):
        username = options['username']
        current_user_username = options['current_user']

        # Check if the user running the command is an admin
        try:
            current_user = User.objects.get(username=current_user_username)
            if not current_user.is_staff:
                self.stdout.write(self.style.ERROR('You must be an admin to run this command.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {current_user_username} does not exist.'))
            return

        # Promote the specified user to an admin
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} is now an admin.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))
            
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create Super User'
    """
    To create a new user in the HeartLeaf system

    Command
    ------------------------------------------------------------
    Prerequisites:
        Server Environment variables:
            HEARTLEAF_POSTGRES_NAME=<database name>
            HEARTLEAF_POSTGRES_PORT=<port>
            HEARTLEAF_POSTGRES_HOST=<host>
            HEARTLEAF_POSTGRES_USER=<database user>
            HEARTLEAF_POSTGRES_PASSWORD=<password>

    python manage.py create_user <username> <email> <password> <first_last> <last_name>

    """

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)

    def handle(self, *args, **kwargs):
        # Create user and save to the database
        user = User.objects.create_user(kwargs['username'],
                                        kwargs['email'],
                                        kwargs['password'])

        # Update fields and then save again
        user.first_name = kwargs['first_name']
        user.last_name = kwargs['last_name']
        # make the user staff
        user.is_staff = True
        # make this account super
        # give the user access to the admin section
        user.is_admin = True

        # persist the user
        user.save()

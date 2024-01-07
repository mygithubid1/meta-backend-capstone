from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from restaurant.models import MenuItem


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('makemigrations')
        call_command('migrate')
        User.objects.all().delete()
        User.objects.create_superuser(username='admin',
                                      password='password',
                                      email='admin@domain.com')
        for i in range(5):
            username = slugify(f'user-{i}')
            User.objects.create_user(username=username,
                                     email=f'{username}@domain.com',
                                     password=f'password-{i}')
        for i in range(10):
            MenuItem.objects.create(title=f'Menu item #{i}',
                                    inventory=i + 10,
                                    price=Decimal('10') + i)

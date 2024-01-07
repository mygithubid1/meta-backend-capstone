from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils.timezone import make_aware

from restaurant.models import Booking, MenuItem


class BookingModelTest(TestCase):
    def test_create(self):
        created_booking = Booking.objects.create(name='Guest 1',
                                                 no_of_guests=2,
                                                 booking_date=make_aware(datetime.utcnow()))
        self.assertIsInstance(created_booking.id, int)
        self.assertGreaterEqual(created_booking.id, 1)
        self.assertEquals(Booking.objects.get(pk=created_booking.pk), created_booking)


class MenuItemModelTest(TestCase):
    def test_create(self):
        created_menuitem = MenuItem.objects.create(title='Title 1',
                                                   price=Decimal('20.25'),
                                                   inventory=200)
        self.assertIsInstance(created_menuitem.id, int)
        self.assertGreaterEqual(created_menuitem.id, 1)
        self.assertEquals(MenuItem.objects.get(pk=created_menuitem.pk), created_menuitem)

from datetime import datetime, timedelta
from decimal import Decimal
from http import HTTPStatus

from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from restaurant.models import Booking, MenuItem


class AuthenticationAwareTestCase(APITestCase):
    def setUp(self):
        get_user_model().objects.all().delete()
        response = self.client.post('/auth/users/', data=dict(username='user-1',
                                                              email='user-1@gmail.com',
                                                              password='password-1'),
                                    format='json')
        self.assertEquals(response.status_code, HTTPStatus.CREATED)
        response = self.client.post(path='/restaurant/api-token-auth/',
                                    data={
                                        'username': 'user-1',
                                        'password': 'password-1'
                                    }, format='json')
        self.assertEquals(response.status_code, HTTPStatus.OK)
        auth_token = response.json().get('token')
        self.assertIsInstance(auth_token, str)
        auth_token = auth_token.strip()
        self.assertGreater(len(auth_token), 0)
        self.auth_token = auth_token

    def tearDown(self):
        response = self.client.post(path=reverse('logout'),
                                    headers={'Authorization': f'Token {self.auth_token}'})
        self.assertEquals(response.status_code, HTTPStatus.NO_CONTENT)


class UnauthorizedMenuItemTest(APITestCase):
    def _compare_menu_items(self, manually_created, from_server):
        self.assertEquals(manually_created.id, from_server['id'])
        self.assertEquals(manually_created.title, from_server['title'])
        self.assertEquals(manually_created.inventory, from_server['inventory'])
        self.assertEquals(Decimal(manually_created.price), Decimal(from_server['price']))

    def test_get_menu_item(self):
        created_menu_items = []
        for i in range(5):
            created_menu_items.append(MenuItem.objects.create(title=f'Menu item #{i}',
                                                              price=i + 10,
                                                              inventory=i + 2))
        for created_menu_item in created_menu_items:
            response = self.client.get(path=f'/restaurant/menu-items/{created_menu_item.id}')
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self._compare_menu_items(created_menu_item, response.json())

    def test_patch_menu_item(self):
        created_menu_item = MenuItem.objects.create(title=f'Menu item',
                                                    price=10,
                                                    inventory=2)
        response = self.client.patch(path=f'/restaurant/menu-items/{created_menu_item.id}',
                                     data={'title': 'New Title'},
                                     format='json')
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(response.json()['title'], 'New Title')
        self.assertEquals(MenuItem.objects.get(pk=created_menu_item.pk).title, 'New Title')
        from_db = MenuItem.objects.get(pk=created_menu_item.pk)
        self.assertEquals(from_db.price, created_menu_item.price)
        self.assertEquals(from_db.inventory, created_menu_item.inventory)

    def test_put_menu_item(self):
        created_menu_item = MenuItem.objects.create(title=f'Menu item',
                                                    price=10,
                                                    inventory=2)
        response = self.client.put(path=f'/restaurant/menu-items/{created_menu_item.id}',
                                   data={'title': 'New Title', 'price': 200, 'inventory': 21},
                                   format='json')
        self.assertEquals(response.status_code, HTTPStatus.OK)
        from_server = response.json()
        self.assertEquals(from_server['title'], 'New Title')
        self.assertEquals(Decimal(from_server['price']), Decimal('200'))
        self.assertEquals(from_server['inventory'], 21)
        from_storage = MenuItem.objects.get(pk=created_menu_item.pk)
        self.assertEquals(from_storage.title, 'New Title')
        self.assertEquals(from_storage.price, Decimal('200'))
        self.assertEquals(from_storage.inventory, 21)

    def test_delete_menu_item(self):
        created_menu_item = MenuItem.objects.create(title=f'Menu item',
                                                    price=10,
                                                    inventory=2)
        response = self.client.delete(path=f'/restaurant/menu-items/{created_menu_item.id}',
                                      format='json')
        self.assertEquals(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(MenuItem.objects.all().filter(pk=created_menu_item.pk).exists())


class AuthorizedMenuItemTest(UnauthorizedMenuItemTest, AuthenticationAwareTestCase):
    def test_get_menu_items(self):
        menu_items_created = []
        for i in range(5):
            menu_items_created.append(MenuItem.objects.create(title=f'Menu item #{i}',
                                                              price=i + 10,
                                                              inventory=i + 2))
        response = self.client.get(path='/restaurant/menu-items/')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.get(path='/restaurant/menu-items/',
                                   headers={'Authorization': f'Token {self.auth_token}'})
        self.assertEquals(response.status_code, HTTPStatus.OK)
        server_menu_items = response.json()
        server_menu_items.sort(key=lambda menu_item: menu_item['id'])
        for retrieved_menu_item, created_menu_item in zip(server_menu_items, menu_items_created):
            self._compare_menu_items(created_menu_item, retrieved_menu_item)

    def test_create_menu_item(self):
        response = self.client.post(path=f'/restaurant/menu-items/',
                                    data={'title': 'New Title', 'price': 200, 'inventory': 21},
                                    format='json')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.post(path=f'/restaurant/menu-items/',
                                    headers={'Authorization': f'Token {self.auth_token}'},
                                    data={'title': 'New Title', 'price': 200, 'inventory': 21},
                                    format='json')
        self.assertEquals(response.status_code, HTTPStatus.CREATED)
        from_server = response.json()
        self.assertEquals(from_server['title'], 'New Title')
        self.assertEquals(Decimal(from_server['price']), Decimal('200'))
        self.assertEquals(from_server['inventory'], 21)
        from_storage = MenuItem.objects.get(pk=from_server['id'])
        self._compare_menu_items(from_storage, from_server)


class BookingTest(AuthenticationAwareTestCase):
    def _compare_bookings(self, from_db, from_server):
        self.assertEquals(from_db.name, from_server['name'])
        self.assertEquals(from_db.no_of_guests, from_server['no_of_guests'])
        self.assertEquals(from_db.booking_date, parse_datetime(from_server['booking_date']))

    def test_get_booking(self):
        bookings = []
        for i in range(5):
            bookings.append(Booking.objects.create(name=f'Name {i}',
                                                   no_of_guests=i + 1,
                                                   booking_date=make_aware(datetime.utcnow() + timedelta(days=1))))
        response = self.client.get(path=f'/restaurant/booking/tables/{bookings[0].id}/')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        for booking in bookings:
            response = self.client.get(path=f'/restaurant/booking/tables/{booking.id}/',
                                       headers={'Authorization': f'Token {self.auth_token}'})
            self.assertEquals(response.status_code, HTTPStatus.OK)
            self._compare_bookings(booking, response.json())

    def test_patch_booking(self):
        created_booking = Booking.objects.create(name=f'Name 0',
                                                 no_of_guests=1,
                                                 booking_date=make_aware(datetime.utcnow()))
        response = self.client.patch(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                     data={'no_of_guests': 2},
                                     format='json')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.patch(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                     headers={'Authorization': f'Token {self.auth_token}'},
                                     data={'no_of_guests': 2},
                                     format='json')
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(response.json()['no_of_guests'], 2)
        from_db = Booking.objects.get(pk=created_booking.pk)
        self.assertEquals(from_db.no_of_guests, 2)
        self.assertEquals(from_db.booking_date, created_booking.booking_date)
        self.assertEquals(from_db.name, created_booking.name)

    def test_put_booking(self):
        created_booking = Booking.objects.create(name=f'Name 0',
                                                 no_of_guests=1,
                                                 booking_date=make_aware(datetime.utcnow()))
        new_date = make_aware(datetime.utcnow())
        response = self.client.put(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                   data={'name': 'New Name 0', 'no_of_guests': 3,
                                         'booking_date': new_date},
                                   format='json')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.put(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                   headers={'Authorization': f'Token {self.auth_token}'},
                                   data={'name': 'New Name 0', 'no_of_guests': 3,
                                         'booking_date': new_date},
                                   format='json')
        self.assertEquals(response.status_code, HTTPStatus.OK)
        from_server = response.json()
        self.assertEquals(from_server['name'], 'New Name 0')
        self.assertEquals(from_server['no_of_guests'], 3)
        self.assertEquals(parse_datetime(from_server['booking_date']), new_date)
        from_storage = Booking.objects.get(pk=created_booking.pk)
        self.assertEquals(from_storage.name, 'New Name 0')
        self.assertEquals(from_storage.no_of_guests, 3)
        self.assertEquals(from_storage.booking_date, new_date)

    def test_delete_booking(self):
        created_booking = Booking.objects.create(name=f'Name 0',
                                                 no_of_guests=1,
                                                 booking_date=make_aware(datetime.utcnow()))
        response = self.client.delete(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                      format='json')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.delete(path=f'/restaurant/booking/tables/{created_booking.id}/',
                                      headers={'Authorization': f'Token {self.auth_token}'},
                                      format='json')
        self.assertEquals(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Booking.objects.all().filter(pk=created_booking.pk).exists())

    def test_get_bookings(self):
        bookings_created = []
        for i in range(5):
            bookings_created.append(Booking.objects.create(name=f'Name {i}',
                                                           no_of_guests=i + 1,
                                                           booking_date=make_aware(
                                                               datetime.utcnow() + timedelta(days=1))))
        response = self.client.get(path=f'/restaurant/booking/tables/')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.get(path=f'/restaurant/booking/tables/',
                                   headers={'Authorization': f'Token {self.auth_token}'})
        self.assertEquals(response.status_code, HTTPStatus.OK)
        server_bookings = response.json()
        server_bookings.sort(key=lambda booking: booking['id'])
        for retrieved_booking, created_booking in zip(server_bookings, bookings_created):
            self._compare_bookings(created_booking, retrieved_booking)

    def test_create_booking(self):
        new_date = make_aware(datetime.utcnow())
        response = self.client.post(path=f'/restaurant/booking/tables/',
                                    data={'name': 'New Name 0', 'no_of_guests': 3,
                                          'booking_date': new_date},
                                    format='json')
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        response = self.client.post(path=f'/restaurant/booking/tables/',
                                    headers={'Authorization': f'Token {self.auth_token}'},
                                    data={'name': 'New Name 0', 'no_of_guests': 3,
                                          'booking_date': new_date},
                                    format='json')
        self.assertEquals(response.status_code, HTTPStatus.CREATED)
        from_server = response.json()
        from_storage = Booking.objects.get(pk=from_server['id'])
        self._compare_bookings(from_storage, from_server)

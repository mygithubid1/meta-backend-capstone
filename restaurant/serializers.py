from rest_framework import fields
from rest_framework.serializers import ModelSerializer

from restaurant.models import MenuItem, Booking


class MenuItemSerializer(ModelSerializer):
    id = fields.IntegerField(read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'


class BookingSerializer(ModelSerializer):
    id = fields.IntegerField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

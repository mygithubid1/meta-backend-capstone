# Create your views here.
from django.shortcuts import render
from rest_framework.generics import DestroyAPIView, UpdateAPIView, CreateAPIView, ListCreateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from restaurant.models import MenuItem, Booking
from restaurant.serializers import MenuItemSerializer, BookingSerializer


# Create your views here.
def index(request):
    return render(request, 'index.html')


class MenuItemsView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


class SingleMenuItemView(RetrieveUpdateAPIView, DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from restaurant.views import BookingViewSet

router = DefaultRouter()
router.register('tables', BookingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurant/', include('restaurant.urls')),
    path('restaurant/booking/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.base')),
]

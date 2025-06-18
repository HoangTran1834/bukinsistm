from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ShiftViewSet, BookingViewSet, AuthViewSet, RouteViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'shift', ShiftViewSet, basename='shift')
router.register(r'booking', BookingViewSet, basename='booking')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'route', RouteViewSet, basename='route')


api_urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
]

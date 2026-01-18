from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ServiceViewSet, RequestViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'requests', RequestViewSet, basename='request')

urlpatterns = [
    path('', include(router.urls)),
]

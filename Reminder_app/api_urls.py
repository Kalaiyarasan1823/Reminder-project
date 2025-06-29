from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ReminderViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

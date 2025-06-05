from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.github_login_view, name='github_login'),
    path('github-success/', views.github_success, name='github_success'),
]

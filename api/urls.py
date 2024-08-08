from django.urls import path
from .views import UserRegisterView, UserDetailView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
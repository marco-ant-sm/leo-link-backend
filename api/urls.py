from django.urls import path
from .views import UserRegisterView, UserDetailView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
from .views import CustomTokenObtainPairView
from .views import GoogleLoginApi
from .views import validate_token

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    # Session tokens
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('validate_token/', validate_token, name='validate_token'),
    #google auth
    path('login/google/', GoogleLoginApi.as_view(), name='google_login'),
]
from django.urls import path, include
from .views import UserRegisterView, UserDetailView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
from .views import CustomTokenObtainPairView
from .views import GoogleLoginApi
from .views import validate_token
from .views import UserProfileView
from rest_framework.documentation import include_docs_urls
from .views import ComentarioListCreateView, ComentarioDetailView
#Crear y eliminar asistencias
from .views import EventoViewSet, asistencia_view

#Librerias para cruds
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet

router = DefaultRouter()
router.register(r'events', EventoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    # Session tokens
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('validate_token/', validate_token, name='validate_token'),
    #google auth
    path('auth/login/google/', GoogleLoginApi.as_view(), name='google_login'),
    #user profile
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    #Documentation
    path('docs/', include_docs_urls(title='LEO API')),
    #Comentarios
    path('eventos/<int:evento_id>/comentarios/', ComentarioListCreateView.as_view(), name='comentarios-list-create'),
    path('eventos/<int:evento_id>/comentarios/<int:pk>/', ComentarioDetailView.as_view(), name='comentario-detail'),
    #Asistencias
    path('events/<int:evento_id>/asistencia/', asistencia_view, name='asistencia_view'),
]
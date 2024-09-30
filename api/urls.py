from django.urls import path, include
from .views import UserRegisterView, UserDetailView, UserListView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
from .views import CustomTokenObtainPairView
from .views import GoogleLoginApi
from .views import validate_token
from .views import UserProfileView, UserDeleteView, UserUpdateView
from rest_framework.documentation import include_docs_urls
from .views import ComentarioListCreateView, ComentarioDetailView
#Crear y eliminar asistencias
from .views import EventoViewSet, asistencia_view
#categorias de eventos 
from api.views import CategoriaEventoListView, get_user_categories, update_user_categories, update_user_profile, update_user_password, RecoverPasswordView, CategoriaEventoPublicoListView
#Notificaciones
from api.views import NotificacionesUsuarioView, MarcarNotificacionesLeidasView

#Librerias para cruds
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet, EventoReadOnlyViewSet

router = DefaultRouter()
router.register(r'events', EventoViewSet)
router.register(r'public-events', EventoReadOnlyViewSet, basename='evento-read-only')

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
    #Categorias de eventos
    path('categories/', CategoriaEventoListView.as_view(), name='categoria_evento_list'),
    path('public-event-categories/', CategoriaEventoPublicoListView.as_view(), name='categoria_evento_publico_list'),
    path('user/categories/', get_user_categories, name='get_user_categories'),
    path('user/update-categories/', update_user_categories, name='update_user_categories'),
    #Notificaciones
    path('notificaciones/', NotificacionesUsuarioView.as_view(), name='notificaciones-usuario'),
    #Marcar notificaciones como leidas
    path('notificaciones/marcar-leidas/', MarcarNotificacionesLeidasView.as_view(), name='marcar-notificaciones-leidas'),
    path('user/update-user-profile/', update_user_profile, name='update_user_profile'),
    path('user/update-password/', update_user_password, name='update_user_password'),
    path('recover-password/', RecoverPasswordView.as_view(), name='recover_password'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
    path('user/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
]
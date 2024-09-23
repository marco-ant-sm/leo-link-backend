from django.shortcuts import render

#Tokens standard log in
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import CustomUserSerializer

#Google auth
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.views import APIView
from .serializers import AuthSerializer
from .services import get_user_data
from .models import CustomUser 
import os

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['nombre'] = user.nombre
        token['apellidos'] = user.apellidos

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# class GoogleLoginApi(APIView):
#     def get(self, request, *args, **kwargs):
#         auth_serializer = AuthSerializer(data=request.GET)
#         auth_serializer.is_valid(raise_exception=True)
        
#         validated_data = auth_serializer.validated_data
#         user_data = get_user_data(validated_data)
        
#         #Validate domain
#         email=user_data['email']
#         if not (email.endswith('@alumnos.udg.mx') or email.endswith('@academicos.udg.mx')):
#             return redirect(f'{settings.BASE_APP_URL}/error', status=403)
        
#         user, _ = CustomUser.objects.get_or_create(
#             email=user_data['email'],
#             defaults={'nombre': user_data.get('first_name'), 'apellidos': user_data.get('last_name')}
#         )
#         login(request, user)

#         return redirect(settings.BASE_APP_URL)


# Register, login and redirection after auth
from urllib.parse import urlencode

# class GoogleLoginApi(APIView):
#     def get(self, request, *args, **kwargs):
#         auth_serializer = AuthSerializer(data=request.GET)
#         auth_serializer.is_valid(raise_exception=True)
        
#         validated_data = auth_serializer.validated_data
#         user_data = get_user_data(validated_data)
        
#         # Validar dominio
#         email = user_data['email']
#         if not (email.endswith('@alumnos.udg.mx') or email.endswith('@academicos.udg.mx')):
#             return JsonResponse({'error': 'Dominio no permitido'}, status=403)
        
#         user, _ = CustomUser.objects.get_or_create(
#             email=user_data['email'],
#             defaults={'nombre': user_data.get('first_name'), 'apellidos': user_data.get('last_name')}
#         )
#         login(request, user)

#         # Preparar datos del usuario para la URL
#         user_info = {
#             'email': user.email,
#             'nombre': user.nombre,
#             'apellidos': user.apellidos,
#         }
#         query_string = urlencode(user_info)
#         redirect_url = f"{settings.BASE_APP_URL}/success?{query_string}"

#         return redirect(redirect_url)

from rest_framework_simplejwt.tokens import RefreshToken

class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)
        
        # Validar dominio
        email = user_data['email']
        if not (email.endswith('@alumnos.udg.mx') or email.endswith('@academicos.udg.mx')):
            return redirect(f'{settings.BASE_APP_URL}/signUp?error=invalid_domain', status=403)
        
         # Asignar permiso_u basado en el dominio del correo
        if email.endswith('@academicos.udg.mx'):
            permiso_u = 'docente'
        elif email.endswith('@alumnos.udg.mx'):
            permiso_u = 'estudiante'
        
        user, _ = CustomUser.objects.get_or_create(
            email=user_data['email'],
            defaults={'nombre': user_data.get('first_name'), 'apellidos': user_data.get('last_name'), 'permiso_u': permiso_u}
        )
        login(request, user)

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Preparar datos del usuario para la URL
        user_info = {
            'nombre': user.nombre,
            'apellidos': user.apellidos,
            'access': access_token,
            'refresh': refresh_token
        }
        query_string = urlencode(user_info)
        redirect_url = f"{settings.BASE_APP_URL}/success?{query_string}"

        return redirect(redirect_url)
    

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework import status

#Verifica si un usuario esta autenticado
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        AccessToken(token)  # Verifica que el token sea válido
        return Response(status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    


#view user profile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user

#Evento crud
from .serializers import EventoSerializer
from .models import Evento, Notificacion
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

#Notificaciones
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from api.serializers import NotificacionSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        # Obtener los eventos ordenados por created_at de manera descendente
        queryset = self.queryset.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
            evento = serializer.save(usuario=self.request.user)
            self.enviar_notificaciones(evento)
    
    def perform_update(self, serializer):
        instance = self.get_object()
        remove_image = self.request.data.get('eliminar_imagen', False)
        new_image = self.request.FILES.get('imagen', None)

        # Caso 2: Eliminar la imagen existente si se seleccionó el checkbox
        if remove_image and instance.imagen:
            instance.imagen.delete()
            instance.imagen = None  # Asegurarse de que la imagen se elimine de la base de datos también

        # Caso 3: Reemplazar la imagen existente por una nueva
        if new_image:
            if instance.imagen:  # Si existe una imagen anterior
                instance.imagen.delete()  # Eliminar la imagen anterior
            instance.imagen = new_image  # Asignar la nueva imagen

        # Caso 1: Agregar o mantener la imagen según lo que se haya subido
        serializer.save(usuario=self.request.user, imagen=instance.imagen)

    def enviar_notificaciones(self, evento):
        # Obtener las categorías del evento
        categorias_evento = evento.categorias.all()
        
        # Buscar usuarios que tengan esas categorías en su perfil
        usuarios_interesados = CustomUser.objects.filter(categorias_preferidas__in=categorias_evento).exclude(id=evento.usuario.id).distinct()

        # Crear una notificación para cada usuario interesado
        for usuario in usuarios_interesados:
            mensaje = f"Se ha agregado { 'una' if str(evento.tipo_e) == 'practica' else 'un' } {str(evento.tipo_e)} de tu interés: {evento.nombre}"
            Notificacion.objects.create(
                usuario=usuario,
                evento=evento,
                mensaje=mensaje,
                tipo_e=evento.tipo_e
            )

            # Notificar en tiempo real a través de WebSocket
            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     f"user_{usuario.id}",  # Cada usuario tendrá su propio grupo de WebSocket
            #     {
            #         'type': 'send_notification',
            #         'message': f"Nuevo elemento de tu interes: {evento.nombre} en la categoría {evento.categoria_p}",
            #     }
            # )

#Comentarios
from rest_framework import generics, permissions
from .models import Comentario
from .serializers import ComentarioSerializer

class ComentarioListCreateView(generics.ListCreateAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        evento_id = self.kwargs['evento_id']
        return Comentario.objects.filter(evento_id=evento_id)

    def perform_create(self, serializer):
        evento_id = self.kwargs['evento_id']
        evento = Evento.objects.get(id=evento_id)
        serializer.save(usuario=self.request.user, evento=evento)
        #serializer.save(usuario=self.request.user)

#Comentarios delete
class ComentarioDetailView(generics.RetrieveDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        evento_id = self.kwargs['evento_id']
        return Comentario.objects.filter(evento_id=evento_id)


#Vista para crear y eliminar asistencias.
from .serializers import AsistenciaSerializer
from .models import Asistencia

@api_view(['POST', 'DELETE'])
def asistencia_view(request, evento_id):
    # Verifica que el usuario esté autenticado
    if not request.user.is_authenticated:
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return Response({'error': 'Evento no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if Asistencia.objects.filter(usuario=request.user, evento=evento).exists():
            return Response({'error': 'Ya has confirmado tu asistencia a este evento'}, status=status.HTTP_400_BAD_REQUEST)
        
        asistencia = Asistencia.objects.create(usuario=request.user, evento=evento)
        serializer = AsistenciaSerializer(asistencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        try:
            asistencia = Asistencia.objects.get(usuario=request.user, evento=evento)
        except Asistencia.DoesNotExist:
            return Response({'error': 'No tienes una asistencia confirmada para este evento'}, status=status.HTTP_404_NOT_FOUND)
        
        asistencia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
#Categorias de eventos
from api.serializers import CategoriaEventoSerializer, CustomUserSerializer
from api.models import CategoriaEvento

#Obtener categorias de eventos
class CategoriaEventoListView(generics.ListAPIView):
    queryset = CategoriaEvento.objects.all()
    serializer_class = CategoriaEventoSerializer

#Obtener categorias de usuario
@api_view(['GET'])
def get_user_categories(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


#Modificar categorias de usuario
@api_view(['PATCH'])
def update_user_categories(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    categorias_ids = request.data.get('categorias_ids', [])

    try:
        categorias = CategoriaEvento.objects.filter(id__in=categorias_ids)
    except CategoriaEvento.DoesNotExist:
        return Response({'detail': 'Some categories do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    user.categorias_preferidas.set(categorias)
    user.save()

    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


#obtener notificaciones
class NotificacionesUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener las notificaciones del usuario autenticado
        notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-created_at')
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)
    
#Marcar notificaciones de usuario como leidas
class MarcarNotificacionesLeidasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Obtener las notificaciones del usuario autenticado
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False)
        
        # Marcar todas las notificaciones como leídas
        notificaciones.update(leida=True)

        return Response({'message': 'Notificaciones marcadas como leídas'}, status=status.HTTP_200_OK)


#Actualizar Perfil del Usuario
@api_view(['PATCH'])
def update_user_profile(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    serializer = CustomUserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        # Manejo para eliminar la imagen
        remove_image = request.data.get('eliminar_imagen', False)
        new_image = request.FILES.get('imagen', None)

        # Eliminar la imagen existente si se seleccionó
        if remove_image and user.imagen:
            if os.path.isfile(user.imagen.path):
                os.remove(user.imagen.path)
            user.imagen = None  # Eliminar de la base de datos

        # Si se proporciona una nueva imagen, manejarla
        if new_image:
            if user.imagen:  # Si ya existe una imagen anterior
                if os.path.isfile(user.imagen.path):
                    os.remove(user.imagen.path)  # Eliminar la imagen anterior
            user.imagen = new_image  # Asignar la nueva imagen

        # Guardar los cambios en el usuario
        serializer.save()  # Guarda los cambios que incluye la descripción y la imagen
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Aquí se informa sobre los errores específicos en la validación
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


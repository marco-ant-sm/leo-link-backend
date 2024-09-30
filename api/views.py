from django.shortcuts import render

#Tokens standard log in
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import serializers

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
    #permission_classes = [permissions.AllowAny]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Llama al método de creación del serializer
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Aquí empieza la lógica para enviar el correo
            subject = 'Registro a Leo-Link'
            password = request.data.get('password')  # Obtén la contraseña temporal
            html_message = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; border-radius: 8px;">
                    <h2 style="color: #2a4d69;">Bienvenido a Leo-Link</h2>
                    <p>Hola {user.nombre},</p>
                    <p>Tu cuenta ha sido creada exitosamente.</p>
                    <p>Tu contraseña temporal es: <strong>{password}</strong></p>
                    <p>Para cambiarla simplemente sigue los siguientes pasos:</p>
                    <ol>
                        <li>Ingresa a tu cuenta.</li>
                        <li>Haz clic en la imagen de usuario que aparece en la barra de navegación en la parte derecha.</li>
                        <li>Selecciona <strong>Configuración</strong>.</li>
                        <li>Dirígete a la pestaña de <strong>Configuración de Usuario</strong>.</li>
                        <li>En esa pestaña encontrarás la opción de <strong>cambiar contraseña</strong>.</li>
                    </ol>
                    <p>Gracias,<br>El equipo de Leo-Link</p>
                </div>
            </body>
            </html>
            """

            # Intenta enviar el correo
            try:
                send_mail(
                    subject,
                    '',  # Deja el cuerpo del texto vacío ya que solo usarás HTML
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                    html_message=html_message
                )
            except Exception as e:
                # Aquí puedes registrar el error en un log si es necesario
                print(f"Error al enviar correo: {e}")

            # Respuesta positiva al usuario
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)


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

#Nuevo validar
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return Response({'message': 'Credenciales incorrectas. Intente nuevamente.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message': 'Error en el servidor. Intente más tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Si las credenciales son válidas, devuelve el token
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
#Viejo Validar
# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer


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
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{usuario.id}",  # Cada usuario tendrá su propio grupo de WebSocket
                {
                    'type': 'send_notification',
                    'message': f"Nuevo elemento de tu interes: {evento.nombre} en la categoría {evento.categoria_p}",
                }
            )

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


#Actualizar contraseña de usuario
@api_view(['PATCH'])
def update_user_password(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not new_password or not confirm_password:
        return Response({'detail': 'Both password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)


#Recuperar Contraseña
from django.core.mail import send_mail

class RecoverPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            # Verifica si el correo existe en la base de datos
            user = CustomUser.objects.get(email=email)

            # Genera el token JWT con una duración de 24 horas
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            # URL para resetear la contraseña
            reset_url = f"http://localhost:3000/recoverPassword?token={token}"

            # Cuerpo del mensaje en HTML
            html_message = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; border-radius: 8px;">
                    <h2 style="color: #2a4d69;">Recuperación de Contraseña</h2>
                    <p>Hola,</p>
                    <p>Solicitaste recuperar tu contraseña. Dirígete al siguiente enlace y sigue los pasos descritos:</p>
                    <a href="{reset_url}" style="display: inline-block; padding: 10px 15px; background-color: #1d70b8; color: white; text-decoration: none; border-radius: 5px;">Recuperar Contraseña</a>
                    <p>Sigue los siguientes pasos:</p>
                    <ol>
                        <li>Ingresa a tu cuenta.</li>
                        <li>Haz clic en la imagen de usuario que aparece en la barra de navegación en la parte derecha.</li>
                        <li>Selecciona <strong>Configuración</strong>.</li>
                        <li>Dirígete a la pestaña de <strong>Configuración de Usuario</strong>.</li>
                        <li>En esa pestaña encontrarás la opción de <strong>cambiar contraseña</strong>.</li>
                    </ol>
                    <p>Si no solicitaste este cambio, por favor ignora este correo.</p>
                    <p>Gracias,<br>El equipo de Leo-Link</p>
                </div>
            </body>
            </html>
            """

            # Envía un correo con el asunto y el mensaje en HTML
            send_mail(
                'Leo-Link: Recuperación de Contraseña',
                '',  # Deja el cuerpo del texto vacío ya que solo usarás HTML
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=html_message  # Cuerpo del correo en formato HTML
            )

            return Response({'message': 'Correo de recuperación enviado.'}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'message': 'El correo no está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

# class RecoverPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         try:
#             # Verifica si el correo existe en la base de datos
#             user = CustomUser.objects.get(email=email)

#             # Genera el token JWT con una duración de 24 horas
#             refresh = RefreshToken.for_user(user)
#             token = str(refresh.access_token)

#             # Envía un correo con el link para la recuperación de contraseña
#             reset_url = f"http://localhost:3000/recoverPassword?token={token}"
#             send_mail(
#                 'Recuperación de Contraseña',
#                 f'Solicitaste recuperar tu contraseña. Haz clic en el siguiente enlace para acceder: {reset_url}',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 fail_silently=False,
#             )

#             return Response({'message': 'Correo de recuperación enviado.'}, status=status.HTTP_200_OK)

#         except CustomUser.DoesNotExist:
#             return Response({'message': 'El correo no está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

#Obtener todos los objetos Usuario
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()

#Eliminar un Usuario especifico
class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return generics.get_object_or_404(CustomUser, id=user_id)
    
#Actualizar usuario mediante id
class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Obtener el objeto basado en el pk (id)
        user_id = self.kwargs['pk']
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if user is None:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#Mostrar eventos publicos
class EventoReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Esto desactiva la autenticación para esta vista

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
#Obtener categorias de eventos publicos
class CategoriaEventoPublicoListView(generics.ListAPIView):
    queryset = CategoriaEvento.objects.all()
    serializer_class = CategoriaEventoSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
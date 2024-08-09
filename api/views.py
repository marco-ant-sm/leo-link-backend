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
        token['email'] = user.email

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
            return redirect(settings.BASE_APP_URL, status=403)
        
        user, _ = CustomUser.objects.get_or_create(
            email=user_data['email'],
            defaults={'nombre': user_data.get('first_name'), 'apellidos': user_data.get('last_name')}
        )
        login(request, user)

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Preparar datos del usuario para la URL
        user_info = {
            'email': user.email,
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        AccessToken(token)  # Verifica que el token sea válido
        return Response(status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_401_UNAUTHORIZED)



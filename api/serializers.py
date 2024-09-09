from rest_framework import serializers
from .models import CustomUser
#Comentario y evento
from .models import Evento, Comentario
from .models import Asistencia, CategoriaEvento


class CategoriaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaEvento
        fields = ['id', 'nombre']



class CustomUserSerializer(serializers.ModelSerializer):
    categorias_preferidas = CategoriaEventoSerializer(many=True, read_only=True)
    categorias_preferidas_ids = serializers.SerializerMethodField()


    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'nombre', 'apellidos', 'password', 'descripcion', 'permiso_u', 'imagen', 'categorias_preferidas', 'categorias_preferidas_ids')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8, 'required': False},
            'imagen': {'required': False}
        }


    def get_categorias_preferidas_ids(self, obj):
        return [categoria.id for categoria in obj.categorias_preferidas.all()]
    

    def create(self, validated_data):
        categorias_preferidas = validated_data.pop('categorias_preferidas', [])
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            apellidos=validated_data.get('apellidos', ''),
            descripcion=validated_data.get('descripcion', ''),
            permiso_u=validated_data.get('permiso_u', 'admin'),
            imagen=validated_data.get('imagen', None)
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        user.categorias_preferidas.set(categorias_preferidas)
        return user

    def update(self, instance, validated_data):
        categorias_preferidas = validated_data.pop('categorias_preferidas', [])
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        instance.categorias_preferidas.set(categorias_preferidas)
        return instance
    

# Google auth
class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

#Comentario serializer
class ComentarioSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comentario
        fields = ['id', 'comentario', 'evento', 'usuario', 'created_at', 'updated_at']
        extra_kwargs = {
            'evento': {'required': False},
            'usuario': {'required': False},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

#Evento serializer
class EventoSerializer(serializers.ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True)
    usuario = CustomUserSerializer(read_only=True)
    categorias = CategoriaEventoSerializer(many=True, read_only=True)
    categorias_ids = serializers.SerializerMethodField()
    numero_asistentes = serializers.SerializerMethodField()
    asistido_por_usuario = serializers.SerializerMethodField()


    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'descripcion', 'usuario', 'comentarios', 'categorias', 'categorias_ids', 'created_at', 'updated_at', 'numero_asistentes', 'asistido_por_usuario', 'imagen']
        read_only_fields = ['usuario', 'created_at', 'updated_at']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True}
        }


    def get_categorias_ids(self, obj):
        return [categoria.id for categoria in obj.categorias.all()]
    
    
    def get_numero_asistentes(self, obj):
        return obj.asistencias.count()
    
    def get_asistido_por_usuario(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Asistencia.objects.filter(usuario=request.user, evento=obj).exists()
        return False


#Asistencia serializer
class AsistenciaSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer(read_only=True)
    evento = EventoSerializer(read_only=True)

    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'evento', 'created_at']
        read_only_fields = ['created_at']
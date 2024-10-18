from rest_framework import serializers
from .models import CustomUser
#Comentario y evento
from .models import Evento, Comentario
from .models import Asistencia, CategoriaEvento, Notificacion
from rest_framework.exceptions import ValidationError


class CategoriaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaEvento
        fields = ['id', 'nombre', 'tipo_e']



class CustomUserSerializer(serializers.ModelSerializer):
    categorias_preferidas = CategoriaEventoSerializer(many=True, read_only=True)
    categorias_preferidas_ids = serializers.SerializerMethodField()


    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'nombre', 'apellidos', 'password', 'descripcion', 'permiso_u', 'imagen', 'categorias_preferidas', 'categorias_preferidas_ids', 'baneo', 'telefono')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8, 'required': False},
            'imagen': {'required': False},
            'baneo': {'required': False},
            'telefono': {'required': False}
        }


    def get_categorias_preferidas_ids(self, obj):
        return [categoria.id for categoria in obj.categorias_preferidas.all()]
    
    def validate_email(self, value):
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este correo ya está registrado.")
            return value
    

    def create(self, validated_data):
    
        categorias_preferidas = validated_data.pop('categorias_preferidas', [])
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            apellidos=validated_data.get('apellidos', ''),
            descripcion=validated_data.get('descripcion', ''),
            permiso_u=validated_data.get('permiso_u', 'admin'),
            imagen=validated_data.get('imagen', None),
            baneo=validated_data.get('baneo', False),
            telefono=validated_data.get('telefono', '')
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
    categoria_p = serializers.CharField(max_length=100, required=False, allow_blank=True)


    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'descripcion', 'usuario', 'comentarios', 'categorias', 'categorias_ids', 'categoria_p', 'created_at', 'updated_at', 'numero_asistentes', 'asistido_por_usuario', 'imagen', 'tipo_e', 'fecha_evento', 'hora_evento', 'host_evento', 'fecha_fin_evento', 'hora_fin_evento', 'lugar_evento', 'disponible', 'fecha_fin_beneficio', 'fecha_fin_descuento', 'horas_practica', 'direccion_practica', 'telefono_practica', 'ayuda_economica_p', 'fecha_fin_practica', 'acceso_e']
        read_only_fields = ['usuario', 'created_at', 'updated_at']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True},
            'fecha_fin_beneficio': {'required': False, 'allow_null': True},
            'fecha_fin_descuento': {'required': False, 'allow_null': True},
            'horas_practica': {'required': False, 'allow_null': True},
            'direccion_practica': {'required': False, 'allow_null': True},
            'telefono_practica': {'required': False, 'allow_null': True},
            'ayuda_economica_p': {'required': False, 'allow_null': True},
            'fecha_fin_practica': {'required': False, 'allow_null': True},
            'acceso_e': {'required': False, 'allow_null': True},
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
    

    #Validar campos dependiendo del evento
    def validate(self, data):
        # Verifica si el tipo de evento es 'evento'
        if data.get('tipo_e') == 'evento':
            # Valida que los campos requeridos no estén vacíos
            if not data.get('fecha_evento'):
                raise serializers.ValidationError("La fecha del evento es obligatoria.")
            if not data.get('hora_evento'):
                raise serializers.ValidationError("La hora del evento es obligatoria.")
            if not data.get('host_evento'):
                raise serializers.ValidationError("El host del evento es obligatorio.")
            if not data.get('fecha_fin_evento'):
                raise serializers.ValidationError("La fecha de finalización es obligatoria.")
            if not data.get('hora_fin_evento'):
                raise serializers.ValidationError("La hora de finalización es obligatoria.")
            if not data.get('lugar_evento'):
                raise serializers.ValidationError("El lugar del evento es obligatorio.")
        
        return data
    

    #Funcion para la correcta asociacion de categorias en la creacion del evento
    def create(self, validated_data):
        
        categoria_p_name = self.context['request'].data.get('categoria_p')
        categorias_ids = self.context['request'].data.get('categorias_ids', [])
        
        
        if not categoria_p_name:
            raise ValidationError("La categoría principal es obligatoria.")

        # Obtén o crea la categoría principal
        categoria_p = CategoriaEvento.objects.filter(nombre=categoria_p_name).first()
        if not categoria_p:
            raise ValidationError("La categoría principal no existe.")

        # Crea el evento
        instance = super().create(validated_data)

        #transformar las categorias en lista
        categorias_ids = categorias_ids.split(',')
        
        # Agrega la categoría principal a la lista de categorías asociadas si no está ya incluida
        categorias_ids = [int(id) for id in categorias_ids if id.isdigit()]

        if categoria_p.id not in categorias_ids:
            categorias_ids.append(categoria_p.id)

        # Configura las categorías del evento
        categorias = CategoriaEvento.objects.filter(id__in=categorias_ids)
        instance.categorias.set(categorias)
        
        # Establece el nombre de la categoría principal
        instance.categoria_p = categoria_p_name
        instance.save()
        
        return instance
    
    #Editar evento
    def update(self, instance, validated_data):
        categoria_p_name = self.context['request'].data.get('categoria_p')
        categorias_ids = self.context['request'].data.get('categorias_ids', [])

        if not categoria_p_name:
            raise ValidationError("La categoría principal es obligatoria.")

        # Obtén o crea la categoría principal
        categoria_p = CategoriaEvento.objects.filter(nombre=categoria_p_name).first()
        if not categoria_p:
            raise ValidationError("La categoría principal no existe.")

        # Actualiza el evento
        instance = super().update(instance, validated_data)

        #transformar las categorias en lista
        categorias_ids = categorias_ids.split(',')

        # Agrega la categoría principal a la lista de categorías asociadas si no está ya incluida
        categorias_ids = [int(id) for id in categorias_ids if id.isdigit()]
        if categoria_p.id not in categorias_ids:
            categorias_ids.append(categoria_p.id)

        # Configura las categorías del evento
        categorias = CategoriaEvento.objects.filter(id__in=categorias_ids)
        instance.categorias.set(categorias)
        
        # Establece el nombre de la categoría principal
        instance.categoria_p = categoria_p_name
        instance.save()
        
        return instance


#Asistencia serializer
class AsistenciaSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer(read_only=True)
    evento = EventoSerializer(read_only=True)

    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'evento', 'created_at']
        read_only_fields = ['created_at']

#Notificaciones
class NotificacionSerializer(serializers.ModelSerializer):
    usuario = CustomUserSerializer(read_only=True)
    evento = EventoSerializer(read_only=True)
    class Meta:
        model = Notificacion
        fields = ['usuario', 'evento', 'mensaje', 'leida', 'created_at', 'tipo_e']
        read_only_fields = ['usuario', 'evento']
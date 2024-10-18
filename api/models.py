from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os

# Create your models here.


#Categorias de eventos
class CategoriaEvento(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('evento', 'Evento'),
        ('practica', 'Práctica'),
        ('beneficio', 'Beneficio'),
        ('descuento', 'Descuento'),
    ]

    nombre = models.CharField(max_length=50, unique=True)
    tipo_e = models.CharField(max_length=10, choices=TIPO_EVENTO_CHOICES, default='evento')
    
    def __str__(self):
        return self.nombre


#Funcion para crear nombres de imagenes unicos
def user_image_upload_path(instance, filename):
    # Obtener la extensión del archivo
    extension = os.path.splitext(filename)[1]
    # Crear un nombre único usando la fecha y hora actuales y el nombre del archivo original
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    # Crear un nombre seguro y limpio para la imagen
    safe_filename = slugify(os.path.splitext(filename)[0])
    # Combinar timestamp y nombre seguro con la extensión original
    new_filename = f"{timestamp}_{safe_filename}{extension}"
    return os.path.join('user_images', new_filename)    

#Usuarios
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=30)
    apellidos = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)  # Hacer la contraseña opcional
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # user permissions
    descripcion = models.TextField(blank=True, null=True, validators=[MaxLengthValidator(800)])
    PERMISO_CHOICES = [
        ('admin', 'Admin'),
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('empresa', 'Empresa'),
        ('grupo_personal', 'Grupo/Personal'),
    ]
    permiso_u = models.CharField(max_length=20, choices=PERMISO_CHOICES, default='admin')
    imagen = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    categorias_preferidas = models.ManyToManyField(CategoriaEvento, blank=True, related_name='usuarios')
    baneo = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email
    
    def delete(self, *args, **kwargs):
        # Si existe una imagen, elimina el archivo antes de eliminar el usuario
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

#Funcion para crear nombres de imagenes unicos
def event_image_upload_path(instance, filename):
    # Obtener la extensión del archivo
    extension = os.path.splitext(filename)[1]
    # Crear un nombre único usando la fecha y hora actuales y el nombre del archivo original
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    # Crear un nombre seguro y limpio para la imagen (evita caracteres no permitidos)
    safe_filename = slugify(os.path.splitext(filename)[0])
    # Combinar timestamp y nombre seguro con la extensión original
    new_filename = f"{timestamp}_{safe_filename}{extension}"
    # Devolver la ruta final del archivo
    return os.path.join('event_images', new_filename)

# Evento
class Evento(models.Model):
    #Campos generales
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(CustomUser, related_name='eventos', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    categorias = models.ManyToManyField(CategoriaEvento, related_name='eventos')
    categoria_p = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to=event_image_upload_path, blank=True, null=True)

    #Tipo de evento
    TIPO_EVENTO_CHOICES = [
        ('evento', 'Evento'),
        ('practica', 'Práctica Profesional'),
        ('beneficio', 'Beneficio'),
        ('descuento', 'Descuento'),
    ]
    tipo_e = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default='evento')

    #Campos de tipo Evento
    fecha_evento = models.DateField(null=True, blank=True)
    hora_evento = models.TimeField(null=True, blank=True)
    host_evento_choices = [
        ('Cucei', 'Cucei'),
        ('Empresa', 'Empresa'),
        ('Consejo estudiantil', 'Consejo Estudiantil'),
        ('Docente', 'Docente'),
    ]
    host_evento = models.CharField(max_length=50, choices=host_evento_choices, null=True, blank=True)
    fecha_fin_evento = models.DateField(null=True, blank=True)
    hora_fin_evento = models.TimeField(null=True, blank=True)
    lugar_evento = models.CharField(max_length=255, null=True, blank=True)

    #Campo disponible para confirmación de eventos
    disponible = models.BooleanField(default=True)

    # Campos adicionales para el tipo 'beneficio'
    fecha_fin_beneficio = models.DateField(null=True, blank=True)  # No es obligatoria

    # Campos adicionales para el tipo 'descuento'
    fecha_fin_descuento = models.DateField(null=True, blank=True)  # No es obligatoria

    #Campos adicionales para el tipo 'practica'
    horas_practica = models.PositiveIntegerField(null=True, blank=True)  # Tipo numérico (hasta 6 dígitos)
    direccion_practica = models.CharField(max_length=255, blank=True, null=True)  # Dirección de una empresa
    telefono_practica = models.CharField(max_length=15, blank=True, null=True)  # Teléfono (máximo 15 dígitos)
    ayuda_economica_p = models.CharField(max_length=10, blank=True, null=True)  # Texto para "sí" o "no"
    fecha_fin_practica = models.DateField(null=True, blank=True)  # No es obligatoria

    #Campo para definir si un evento es publico o privado
    # Campo de acceso
    ACCESO_EVENTO_CHOICES = [
        ('publico', 'Público'),
        ('red-universitaria', 'Red Universitaria'),
    ]
    acceso_e = models.CharField(max_length=20, choices=ACCESO_EVENTO_CHOICES, default='red-universitaria')

    def clean(self):
        # Verifica si el tipo es 'evento' y si los campos requeridos están presentes
        if self.tipo_e == 'evento':
            if not self.fecha_evento or not self.hora_evento or not self.host_evento or not self.fecha_fin_evento or not self.hora_fin_evento or not self.lugar_evento:
                raise ValidationError("Todos los campos de evento deben ser completados.")

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Si existe una imagen, elimina el archivo antes de eliminar el evento
        if self.imagen:
            if os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)


# Comentario
class Comentario(models.Model):
    comentario = models.TextField()
    evento = models.ForeignKey(Evento, related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, related_name='comentarios', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.evento}"
    
#Asistencia a eventos
class Asistencia(models.Model):
    usuario = models.ForeignKey(CustomUser, related_name='asistencias', on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, related_name='asistencias', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        unique_together = ('usuario', 'evento')  # Asegura que un usuario no pueda asistir al mismo evento más de una vez

    def __str__(self):
        return f"{self.usuario} asistirá a {self.evento}"
    

#Modelo notificacion
class Notificacion(models.Model):
    usuario = models.ForeignKey(CustomUser, related_name='notificaciones', on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, related_name='notificaciones', on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # Define las mismas opciones que en CategoriaEvento y Evento
    TIPO_EVENTO_CHOICES = [
        ('evento', 'Evento'),
        ('practica', 'Práctica Profesional'),
        ('beneficio', 'Beneficio'),
        ('descuento', 'Descuento'),
    ]
    tipo_e = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default='evento')

    def __str__(self):
        return f"Notificación para {self.usuario} sobre {self.evento}"
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from django.utils.text import slugify
import os

# Create your models here.


#Categorias de eventos
class CategoriaEvento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    

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
    ]
    permiso_u = models.CharField(max_length=20, choices=PERMISO_CHOICES, default='admin')
    imagen = models.ImageField(upload_to='user_images/', blank=True, null=True)
    categorias_preferidas = models.ManyToManyField(CategoriaEvento, blank=True, related_name='usuarios')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email

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
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(CustomUser, related_name='eventos', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    categorias = models.ManyToManyField(CategoriaEvento, related_name='eventos')
    updated_at = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to=event_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.nombre
    
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
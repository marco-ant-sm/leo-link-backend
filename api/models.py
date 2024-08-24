from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator
from django.utils import timezone

# Create your models here.
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

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email


# Evento
class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(CustomUser, related_name='eventos', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


# Comentario
class Comentario(models.Model):
    comentario = models.TextField()
    evento = models.ForeignKey(Evento, related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, related_name='comentarios', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.evento}"
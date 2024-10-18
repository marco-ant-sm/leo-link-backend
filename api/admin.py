from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Evento, Comentario

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'nombre', 'apellidos', 'is_staff', 'is_active', 'permiso_u', 'descripcion')
    list_filter = ('email', 'is_staff', 'is_active', 'permiso_u')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellidos', 'descripcion', 'imagen')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'permiso_u')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellidos', 'password1', 'password2', 'is_staff', 'is_active', 'descripcion', 'permiso_u', 'imagen')}
        ),
    )
    
    search_fields = ('email',)
    ordering = ('email',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

admin.site.register(CustomUser, CustomUserAdmin)

# Evento
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'usuario')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('usuario',)
    ordering = ('-id',)

# Comentario
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('comentario', 'evento', 'usuario', 'created_at')
    search_fields = ('comentario',)
    list_filter = ('evento', 'usuario')
    ordering = ('-created_at',)
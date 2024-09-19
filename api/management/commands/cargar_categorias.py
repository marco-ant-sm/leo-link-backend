from django.core.management.base import BaseCommand
from api.models import CategoriaEvento

class Command(BaseCommand):
    help = 'Carga las categorías de eventos por defecto'

    def handle(self, *args, **kwargs):
        categorias = [
            'Deportivo', 'Salud', 'Recreativo', 'Académico', 'Laboral',
            'Informática', 'Ocio', 'Comercio', 'Química', 'Industrial',
            'Mecánica Eléctrica', 'Electrónica', 'Temático'
        ]

        for categoria in categorias:
            CategoriaEvento.objects.get_or_create(nombre=categoria)

        # Categorías tipo beneficio
        categorias_beneficios = [
            'Becas y ayudas económicas', 'Posgrados y educación continuada', 'Licencias y permisos',
            'Asesoría y orientación', 'Recursos académicos', 'Redes y contactos profesionales',
            'Salud y bienestar', 'Servicios universitarios'
        ]

        for categoria in categorias_beneficios:
            CategoriaEvento.objects.get_or_create(nombre=categoria, defaults={'tipo_e': 'beneficio'})

        self.stdout.write(self.style.SUCCESS('Categorías de eventos cargadas exitosamente.'))
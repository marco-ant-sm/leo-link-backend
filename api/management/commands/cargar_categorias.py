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

        self.stdout.write(self.style.SUCCESS('Categorías de eventos cargadas exitosamente.'))
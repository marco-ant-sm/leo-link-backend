# Generated by Django 5.0.7 on 2024-09-29 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_customuser_baneo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='permiso_u',
            field=models.CharField(choices=[('admin', 'Admin'), ('estudiante', 'Estudiante'), ('docente', 'Docente'), ('empresa', 'Empresa'), ('grupo_personal', 'Grupo/Personal')], default='admin', max_length=20),
        ),
    ]

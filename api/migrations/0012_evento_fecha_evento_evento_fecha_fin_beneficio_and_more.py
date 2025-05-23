# Generated by Django 5.0.7 on 2024-09-13 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_evento_tipo_e'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='fecha_evento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='fecha_fin_beneficio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='fecha_fin_evento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='hora_evento',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='hora_fin_evento',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='host_evento',
            field=models.CharField(blank=True, choices=[('Cucei', 'Cucei'), ('Empresa', 'Empresa'), ('Consejo estudiantil', 'Consejo Estudiantil'), ('Docente', 'Docente')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='lugar_evento',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

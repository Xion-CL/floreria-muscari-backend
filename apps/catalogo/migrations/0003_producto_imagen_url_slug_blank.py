from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen_principal',
            field=models.ImageField(blank=True, upload_to='productos/'),
        ),
        migrations.AddField(
            model_name='producto',
            name='imagen_url',
            field=models.URLField(blank=True, help_text='Alternativa a subir un archivo: enlace público de la imagen (https://...)', max_length=500, verbose_name='URL de imagen'),
        ),
    ]

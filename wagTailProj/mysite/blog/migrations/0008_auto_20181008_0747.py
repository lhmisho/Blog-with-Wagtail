# Generated by Django 2.0.9 on 2018-10-08 07:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20181008_0542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpagegalleryimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a+', to='wagtailimages.Image'),
        ),
    ]

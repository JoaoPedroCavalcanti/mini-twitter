# Generated by Django 5.1.2 on 2024-10-21 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_postmodel_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postmodel',
            name='image',
        ),
    ]

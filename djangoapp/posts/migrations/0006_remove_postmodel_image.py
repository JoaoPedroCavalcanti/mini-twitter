# Generated by Django 5.1.2 on 2024-10-22 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_postmodel_liked_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postmodel',
            name='image',
        ),
    ]

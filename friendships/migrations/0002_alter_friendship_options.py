# Generated by Django 4.0.5 on 2022-06-26 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friendships', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='friendship',
            options={'ordering': ('-created_at',)},
        ),
    ]

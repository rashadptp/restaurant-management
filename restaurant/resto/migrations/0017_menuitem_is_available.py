# Generated by Django 5.0.6 on 2024-07-03 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resto', '0016_alter_table_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]

# Generated by Django 5.0.6 on 2024-07-02 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resto', '0014_alter_table_id_alter_table_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

# Generated by Django 5.0.6 on 2024-07-03 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resto', '0019_alter_menuitem_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]

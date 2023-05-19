# Generated by Django 4.1.7 on 2023-04-11 14:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='city',
            field=models.CharField(default='null', max_length=200),
        ),
        migrations.AddField(
            model_name='listing',
            name='county',
            field=models.CharField(default='null', max_length=200),
        ),
        migrations.AddField(
            model_name='listing',
            name='url',
            field=models.URLField(default='null'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='date_added_to_db',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='listing',
            name='date_listed',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
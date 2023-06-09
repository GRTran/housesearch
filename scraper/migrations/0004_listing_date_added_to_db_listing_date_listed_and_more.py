# Generated by Django 4.1.7 on 2023-04-27 17:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0003_alter_listing_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='date_added_to_db',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='listing',
            name='date_listed',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='listing',
            name='reduced',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='listing',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]

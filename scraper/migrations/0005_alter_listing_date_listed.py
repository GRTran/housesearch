# Generated by Django 4.1.7 on 2023-04-28 16:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0004_listing_date_added_to_db_listing_date_listed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='date_listed',
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]
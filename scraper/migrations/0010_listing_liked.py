# Generated by Django 4.1.7 on 2023-06-11 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0009_remove_listing_liked'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='liked',
            field=models.BooleanField(default=0),
        ),
    ]

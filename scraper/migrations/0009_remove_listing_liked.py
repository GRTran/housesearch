# Generated by Django 4.1.7 on 2023-05-13 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0008_listing_liked_liked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='liked',
        ),
    ]

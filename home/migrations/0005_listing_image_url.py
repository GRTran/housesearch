# Generated by Django 4.1.7 on 2023-04-11 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_listing_city_alter_listing_county_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='image_url',
            field=models.URLField(default='', max_length=400),
        ),
    ]

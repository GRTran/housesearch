# Generated by Django 4.1.7 on 2023-04-28 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0005_alter_listing_date_listed'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='region_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

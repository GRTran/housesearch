# Generated by Django 4.1.7 on 2023-10-09 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0006_delete_listing'),
    ]

    operations = [
        migrations.CreateModel(
            name='URLs',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('search_url', models.URLField()),
            ],
        ),
    ]

# Generated by Django 2.2.24 on 2022-05-18 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta_translations', '0005_wikitranslation_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseblockdata',
            name='parsed_keys',
            field=models.TextField(default=None),
        ),
    ]

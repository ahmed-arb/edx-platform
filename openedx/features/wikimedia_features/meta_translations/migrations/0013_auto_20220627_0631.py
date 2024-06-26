# Generated by Django 2.2.24 on 2022-06-27 06:31

from django.db import migrations
import jsonfield.encoder
import jsonfield.fields
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('meta_translations', '0012_courseblock_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseblock',
            name='parent_id',
            field=opaque_keys.edx.django.models.UsageKeyField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='courseblock',
            name='lang',
            field=jsonfield.fields.JSONField(blank=True, default='[]', dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}),
        ),
    ]

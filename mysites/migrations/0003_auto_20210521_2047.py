# Generated by Django 3.1.6 on 2021-05-21 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mysites', '0002_auto_20210518_2058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['date_time'], 'permissions': (('can_comment', 'Can_comment'),)},
        ),
    ]

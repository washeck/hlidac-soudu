# Generated by Django 3.2b1 on 2021-03-14 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hlidac', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rizeni',
            name='predmet',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]

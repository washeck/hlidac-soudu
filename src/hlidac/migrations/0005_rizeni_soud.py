# Generated by Django 3.2b1 on 2021-03-15 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hlidac', '0004_rizeni_probehlo_odvolani'),
    ]

    operations = [
        migrations.AddField(
            model_name='rizeni',
            name='soud',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]

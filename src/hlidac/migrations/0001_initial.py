# Generated by Django 3.2b1 on 2021-03-10 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Rizeni",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spisova_znacka", models.CharField(max_length=20)),
                ("url", models.URLField()),
            ],
        ),
    ]
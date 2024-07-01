# Generated by Django 5.0.6 on 2024-06-19 09:32

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Aeroppp", "0017_alter_task_deadline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="deadline",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 22, 9, 32, 48, 635469, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.CreateModel(
            name="UserLoginStatus",
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
                ("is_logged_in", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

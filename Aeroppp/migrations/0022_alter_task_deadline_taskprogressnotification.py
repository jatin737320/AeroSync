# Generated by Django 5.0.6 on 2024-06-27 19:39

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Aeroppp", "0021_alter_task_deadline_taskupdatenotification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="deadline",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 6, 30, 19, 39, 52, 358986, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.CreateModel(
            name="TaskProgressNotification",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read", models.BooleanField(default=False)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Aeroppp.task"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

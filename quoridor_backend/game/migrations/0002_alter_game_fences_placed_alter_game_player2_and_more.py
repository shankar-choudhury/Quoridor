# Generated by Django 5.2 on 2025-04-09 17:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="fences_placed",
            field=models.JSONField(
                default=list, help_text="List of dictionaries with x,y,orientation"
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="player2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="player2_games",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="winner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="won_games",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

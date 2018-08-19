# Generated by Django 2.0 on 2018-08-19 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0041_add_private_personal_team_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Country'),
        ),
    ]
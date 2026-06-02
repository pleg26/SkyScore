# Generated manually to stabilize initial project bootstrap

import season.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('PARAMOTOR', 'Paramotor'), ('MICROLIGHT', 'Microlight')], max_length=20)),
                ('subtype', models.CharField(choices=[('CLASSIC', 'Classic'), ('SLALOM', 'Slalom'), ('STOL', 'STOL')], max_length=20)),
                ('year', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True, help_text='Optional description of the season.')),
                ('start_date', models.DateField(default=season.models.default_start_date)),
                ('end_date', models.DateField(default=season.models.default_end_date)),
                ('is_active', models.BooleanField(default=False, help_text='Only one season can be active at a time per administrator.')),
            ],
            options={
                'verbose_name': 'Season',
                'verbose_name_plural': 'Seasons',
                'unique_together': {('type', 'subtype', 'year')},
            },
        ),
    ]

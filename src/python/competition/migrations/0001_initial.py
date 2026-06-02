# Generated manually for initial competition model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('season', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('type', models.CharField(choices=[('PARAMOTOR', 'Paramotor'), ('MICROLIGHT', 'Microlight')], max_length=20)),
                ('subtype', models.CharField(choices=[('CLASSIC', 'Classic'), ('SLALOM', 'Slalom'), ('STOL', 'STOL')], max_length=20)),
                ('competition_date', models.DateField()),
                ('season', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='season.season')),
            ],
            options={
                'verbose_name': 'Competition',
                'verbose_name_plural': 'Competitions',
            },
        ),
    ]

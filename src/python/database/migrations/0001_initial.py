from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('competition', '0005_alter_airfield_unique_together_airfield_lon_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Country',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('iso3', models.CharField(max_length=3)),
                        ('name', models.CharField(max_length=100)),
                    ],
                    options={
                        'verbose_name': 'Country',
                        'verbose_name_plural': 'Countries',
                        'ordering': ['iso3'],
                        'db_table': 'competition_country',
                    },
                ),
                migrations.CreateModel(
                    name='Airfield',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('code', models.CharField(max_length=6)),
                        ('name', models.CharField(max_length=50)),
                        ('lon', models.FloatField(default=0)),
                        ('lat', models.FloatField(default=0)),
                        ('alt', models.IntegerField(default=0)),
                        ('country', models.ForeignKey(default=66, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='airfields', to='database.country')),
                    ],
                    options={
                        'verbose_name': 'Airfield',
                        'verbose_name_plural': 'Airfields',
                        'ordering': ['country', 'code'],
                        'db_table': 'competition_airfield',
                    },
                ),
            ],
        ),
    ]

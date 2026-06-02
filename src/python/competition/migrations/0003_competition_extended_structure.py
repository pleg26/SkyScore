import django.db.models.deletion
from django.db import migrations, models


def migrate_existing_competitions(apps, schema_editor):
    Competition = apps.get_model('competition', 'Competition')
    Country = apps.get_model('competition', 'Country')
    Airfield = apps.get_model('competition', 'Airfield')

    unknown_country, _ = Country.objects.get_or_create(
        code='UNK',
        defaults={'name': 'Unknown'},
    )
    unknown_airfield, _ = Airfield.objects.get_or_create(
        name='Unknown airfield',
        country=unknown_country,
    )

    for competition in Competition.objects.all():
        competition.level = competition.level or 'NATIONAL'
        competition.sub_level = competition.sub_level or 'OPEN'
        competition.start_date = competition.start_date or competition.competition_date
        competition.end_date = competition.end_date or competition.competition_date
        competition.country = competition.country or unknown_country
        competition.airfield = competition.airfield or unknown_airfield
        competition.save(
            update_fields=['level', 'sub_level', 'start_date', 'end_date', 'country', 'airfield']
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_competition_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=3, unique=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'Deck',
                'verbose_name_plural': 'Decks',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='NFZ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'No Fly Zone',
                'verbose_name_plural': 'No Fly Zones',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Competitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitors', to='competition.country')),
            ],
            options={
                'verbose_name': 'Competitor',
                'verbose_name_plural': 'Competitors',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Airfield',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='airfields', to='competition.country')),
            ],
            options={
                'verbose_name': 'Airfield',
                'verbose_name_plural': 'Airfields',
                'ordering': ['name'],
                'unique_together': {('name', 'country')},
            },
        ),
        migrations.AddField(
            model_name='competition',
            name='airfield',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='competition.airfield'),
        ),
        migrations.AddField(
            model_name='competition',
            name='competitors',
            field=models.ManyToManyField(blank=True, related_name='competitions', to='competition.competitor'),
        ),
        migrations.AddField(
            model_name='competition',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='competition.country'),
        ),
        migrations.AddField(
            model_name='competition',
            name='decks',
            field=models.ManyToManyField(blank=True, related_name='competitions', to='competition.deck'),
        ),
        migrations.AddField(
            model_name='competition',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='level',
            field=models.CharField(blank=True, choices=[('WORLD', 'World'), ('NATIONAL', 'National')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='nfzs',
            field=models.ManyToManyField(blank=True, related_name='competitions', to='competition.nfz'),
        ),
        migrations.AddField(
            model_name='competition',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='sub_level',
            field=models.CharField(blank=True, choices=[('CHAMPIONSHIP', 'Championship'), ('CUP', 'Cup'), ('OPEN', 'Open')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='competitions', to='competition.task'),
        ),
        migrations.RunPython(migrate_existing_competitions, noop_reverse),
        migrations.RemoveField(
            model_name='competition',
            name='competition_date',
        ),
        migrations.AlterField(
            model_name='competition',
            name='airfield',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='competition.airfield'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='competition.country'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='competition',
            name='level',
            field=models.CharField(choices=[('WORLD', 'World'), ('NATIONAL', 'National')], max_length=20),
        ),
        migrations.AlterField(
            model_name='competition',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='competition',
            name='sub_level',
            field=models.CharField(choices=[('CHAMPIONSHIP', 'Championship'), ('CUP', 'Cup'), ('OPEN', 'Open')], max_length=20),
        ),
        migrations.AlterModelOptions(
            name='competition',
            options={'ordering': ['start_date'], 'verbose_name': 'Competition', 'verbose_name_plural': 'Competitions'},
        ),
    ]

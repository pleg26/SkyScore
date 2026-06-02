import django.db.models.deletion
from django.db import migrations, models


def forward_fill_country_airfield(apps, schema_editor):
    Country = apps.get_model('competition', 'Country')
    Airfield = apps.get_model('competition', 'Airfield')
    Competition = apps.get_model('competition', 'Competition')
    Competitor = apps.get_model('competition', 'Competitor')

    unknown_country = Country.objects.filter(name='Unknown').first()
    if unknown_country is None:
        unknown_country = Country.objects.create(name='Unknown', iso3='UNK')
    elif not unknown_country.iso3:
        unknown_country.iso3 = 'UNK'
        unknown_country.save(update_fields=['iso3'])

    for country in Country.objects.filter(iso3__isnull=True):
        if country.pk == unknown_country.pk:
            continue
        country.iso3 = f'U{country.pk:02d}'[-3:]
        country.save(update_fields=['iso3'])

    for airfield in Airfield.objects.all():
        if not airfield.code:
            airfield.code = f'AF{airfield.pk:04d}'
            airfield.save(update_fields=['code'])

    unknown_airfield = Airfield.objects.filter(name='Unknown airfield', country=unknown_country).first()
    if unknown_airfield is None:
        unknown_airfield = Airfield.objects.create(
            code='AF0000',
            name='Unknown airfield',
            country=unknown_country,
            lat=0,
            long=0,
            alt=0,
        )
    elif not unknown_airfield.code:
        unknown_airfield.code = 'AF0000'
        unknown_airfield.save(update_fields=['code'])

    Airfield.objects.filter(country__isnull=True).update(country=unknown_country)

    Competition.objects.filter(country__isnull=True).update(country=unknown_country)
    Competition.objects.filter(airfield__isnull=True).update(airfield=unknown_airfield)

    Competitor.objects.filter(country__isnull=True).update(country=unknown_country)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_competition_extended_structure'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='iso3',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.RemoveField(
            model_name='country',
            name='code',
        ),
        migrations.AddField(
            model_name='airfield',
            name='alt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='airfield',
            name='code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='airfield',
            name='lat',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='airfield',
            name='long',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='airfield',
            name='country',
            field=models.ForeignKey(default=66, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='airfields', to='competition.country'),
        ),
        migrations.AlterField(
            model_name='airfield',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterModelOptions(
            name='airfield',
            options={'ordering': ['country', 'code'], 'verbose_name': 'Airfield', 'verbose_name_plural': 'Airfields'},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['iso3'], 'verbose_name': 'Country', 'verbose_name_plural': 'Countries'},
        ),
        migrations.RunPython(forward_fill_country_airfield, noop_reverse),
        migrations.AlterField(
            model_name='country',
            name='iso3',
            field=models.CharField(max_length=3),
        ),
        migrations.AlterField(
            model_name='airfield',
            name='code',
            field=models.CharField(max_length=6),
        ),
    ]

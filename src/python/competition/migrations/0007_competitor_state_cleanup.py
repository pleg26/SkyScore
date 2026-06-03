from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0012_competitor_club_competitor_fai_licence_number_and_more'),
        ('competition', '0006_move_country_airfield_to_database_app'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='competition',
                    name='competitors',
                    field=models.ManyToManyField(blank=True, related_name='competitions', to='database.competitor'),
                ),
                migrations.DeleteModel(
                    name='Competitor',
                ),
            ],
        ),
    ]

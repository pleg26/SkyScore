from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
        ('competition', '0005_alter_airfield_unique_together_airfield_lon_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='competitor',
                    name='country',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitors', to='database.country'),
                ),
                migrations.AlterField(
                    model_name='competition',
                    name='country',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='database.country'),
                ),
                migrations.AlterField(
                    model_name='competition',
                    name='airfield',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='database.airfield'),
                ),
                migrations.DeleteModel(
                    name='Airfield',
                ),
                migrations.DeleteModel(
                    name='Country',
                ),
            ],
        ),
    ]

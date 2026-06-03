from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Competitor',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('first_name', models.CharField(max_length=100)),
                        ('last_name', models.CharField(max_length=100)),
                        ('user', models.OneToOneField(blank=True, limit_choices_to={'role': 'PIL'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitor_profile', to=settings.AUTH_USER_MODEL)),
                        ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitors', to='database.country')),
                    ],
                    options={
                        'verbose_name': 'Competitor',
                        'verbose_name_plural': 'Competitors',
                        'ordering': ['last_name', 'first_name'],
                        'db_table': 'competition_competitor',
                    },
                ),
            ],
        ),
    ]

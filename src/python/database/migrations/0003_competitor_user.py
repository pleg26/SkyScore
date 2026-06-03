from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_competitor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AddField(
                    model_name='competitor',
                    name='user',
                    field=models.OneToOneField(blank=True, limit_choices_to={'role': 'PIL'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitor_profile', to=settings.AUTH_USER_MODEL),
                ),
            ],
            state_operations=[],
        ),
    ]

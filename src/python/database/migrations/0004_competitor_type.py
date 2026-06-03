from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_competitor_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitor',
            name='competitor_type',
            field=models.CharField(choices=[('PILOT', 'Pilot'), ('NAVIGATOR', 'Navigator')], default='PILOT', max_length=10),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='competitor_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]

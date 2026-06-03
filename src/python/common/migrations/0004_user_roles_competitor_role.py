from django.db import migrations, models


def migrate_roles_to_competitor(apps, schema_editor):
    User = apps.get_model('common', 'User')

    for user in User.objects.all():
        changed = False

        role = (user.role or 'PUB').strip().upper()
        if role == 'PIL':
            role = 'COMP'
            changed = True

        roles = []
        for role_item in user.roles or []:
            item = str(role_item).strip().upper()
            if item == 'PIL':
                item = 'COMP'
            if item and item not in roles and item != role:
                roles.append(item)

        if user.role != role or user.roles != roles:
            user.role = role
            user.roles = roles
            user.save(update_fields=['role', 'roles'])


def reverse_roles_to_pilot(apps, schema_editor):
    User = apps.get_model('common', 'User')

    for user in User.objects.all():
        changed = False

        role = (user.role or 'PUB').strip().upper()
        if role == 'COMP':
            role = 'PIL'
            changed = True

        roles = []
        for role_item in user.roles or []:
            item = str(role_item).strip().upper()
            if item == 'COMP':
                item = 'PIL'
            if item and item not in roles and item != role:
                roles.append(item)

        if changed or user.roles != roles:
            user.role = role
            user.roles = roles
            user.save(update_fields=['role', 'roles'])


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADM', 'Administrator'), ('ORG', 'Organizer'), ('COMP', 'Competitor'), ('JUD', 'Judge'), ('PUB', 'Public')], default='PUB', max_length=4),
        ),
        migrations.RunPython(migrate_roles_to_competitor, reverse_roles_to_pilot),
    ]

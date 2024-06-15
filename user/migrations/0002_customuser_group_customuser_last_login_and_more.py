# Generated by Django 4.2 on 2024-06-14 14:55

import django.db.models.deletion
from django.db import migrations, models


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    normal_user_group, created = Group.objects.get_or_create(name='normal')
    OAuth2_user_group, created = Group.objects.get_or_create(name='OAuth2')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='group',
            field=models.ForeignKey(default=None, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL, to='auth.group'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.RunPython(create_groups),
    ]

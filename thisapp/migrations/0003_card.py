# Generated by Django 4.2 on 2024-07-03 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thisapp', '0002_invitation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('content', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(0, 'Backlog'), (1, 'In progress'), (3, 'Done')], default=0)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='thisapp.board')),
            ],
        ),
    ]

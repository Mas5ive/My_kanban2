# Generated by Django 4.2 on 2024-06-26 18:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('thisapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='invitations', to='thisapp.board')),
                ('user_recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                     related_name='received_invitations', to=settings.AUTH_USER_MODEL)),
                ('user_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='sent_invitations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='invitation',
            constraint=models.CheckConstraint(check=models.Q(('user_sender', models.F(
                'user_recipient')), _negated=True), name='check_user_sender_not_recipient'),
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together={('user_recipient', 'board')},
        ),
    ]

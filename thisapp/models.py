import os

from django.db import models

from thisapp.validators import validate_file_size
from user.models import CustomUser


class Board(models.Model):
    title = models.CharField(max_length=32)
    members = models.ManyToManyField(CustomUser, through="Membership")

    def __str__(self):
        return self.title


class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user.username} in {self.board.title}'


class Invitation(models.Model):
    user_recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_invitations')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='invitations')
    user_sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_invitations')

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(user_sender=models.F('user_recipient')),
                                   name='check_user_sender_not_recipient'),
        ]
        unique_together = (('user_recipient', 'board'),)

    def __str__(self) -> str:
        return f'for {self.user_recipient} to {self.board}'


class Card(models.Model):
    class Status(models.IntegerChoices):
        BACKLOG = 1, 'Backlog'
        IN_PROGRESS = 2, 'In progress'
        DONE = 3, 'Done'

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='cards')
    title = models.TextField()
    content = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.BACKLOG)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='own_comments')
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    file = models.FileField(
        upload_to='user_uploads',
        validators=[validate_file_size],
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.card)

    def get_filename(self) -> str | None:
        if self.file:
            return os.path.basename(self.file.path)

    def delete(self, *args, **kwargs):
        if self.file:
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

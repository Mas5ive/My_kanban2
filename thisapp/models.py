import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from thisapp.validators import validate_file
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
        validators=[validate_file],
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.card)

    def get_filename(self) -> str | None:
        if self.file:
            return os.path.basename(self.file.path)

    def get_file_url(self) -> str | None:
        if self.file:
            return reverse('get_file_from_comment', kwargs={
                'board_id': self.card.board.id,
                'card_id': self.card.id,
                'comment_id': self.id
            })
        return None


@receiver(post_delete, sender=Comment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes a file from the file system when its corresponding comment is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

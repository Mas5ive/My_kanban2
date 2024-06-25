from django.db import models

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

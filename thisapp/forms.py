from django import forms

from .models import Board


class CreateBoardForm(forms.ModelForm):
    ...

    class Meta:
        model = Board
        fields = ['title']

from django import forms

from .models import Board, Card


class CreateBoardForm(forms.ModelForm):
    ...

    class Meta:
        model = Board
        fields = ['title']


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'content']
        widgets = {
            'title': forms.Textarea(attrs={'class': 'card-title', 'placeholder': 'Enter title', 'required': True}),
            'content': forms.Textarea(attrs={'class': 'card-content', 'placeholder': 'Enter content'})
        }

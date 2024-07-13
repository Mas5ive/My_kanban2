from django import forms

from .models import Board, Card, Comment


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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'file']
        labels = {
            'file': 'Upload the file up to 50 MB.'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'comment-input',
                'placeholder': 'Enter a comment',
                'required': True}
            )
        }

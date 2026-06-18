from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'Type a message...',
                'class': 'message-input-field',
                'style': 'resize: none; overflow: hidden;'
            })
        }

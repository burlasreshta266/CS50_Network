from .models import Post
from django import forms

class createPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
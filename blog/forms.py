from .models import Post
from django import forms

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','content')
        widgets = {
          'content': forms.Textarea(attrs={'rows':20, 'cols':15}),
        }
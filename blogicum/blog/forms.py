from django.contrib.auth.forms import UserChangeForm
from django import forms
from blog.models import Comment
from blog.models import Post
from blog.models import User


class UserUpdateForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("title", "text", "image", "location", "category", "pub_date")

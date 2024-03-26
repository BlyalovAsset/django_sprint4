from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models import QuerySet
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm
from .forms import PostForm
from .forms import UserUpdateForm
from .models import Category
from .models import Comment
from .models import Post
from .models import User
from .mixins import PaginateMixin
from .mixins import DispatchPostMixin
from .mixins import DispatchCommentMixin


def author_selected(username_required) -> User:

    return get_object_or_404(User, username=username_required)


def posts_just_selected() -> QuerySet:

    return Post.objects.select_related(
        "category", "location", "author").order_by(
        "-pub_date"
    )


def posts_selected() -> QuerySet:

    return (
        posts_just_selected()
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        .annotate(comment_count=Count("comments"))
    )


def posts_selected_with_unpublished_and_future() -> QuerySet:

    return (
        posts_just_selected()
        .annotate(comment_count=Count("comments"))
    )


class IndexView(PaginateMixin, ListView):

    template_name = "blog/index.html"

    def get_queryset(self) -> QuerySet:
        return posts_selected()


class CategoryView(PaginateMixin, ListView):

    template_name = "blog/category.html"

    def get_queryset(self) -> QuerySet:
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"])
        if not category.is_published:
            raise Http404
        return (
            posts_selected_with_unpublished_and_future()
            .filter(
                category=category,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .annotate(comment_count=Count("comments"))
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs["category_slug"]
        )
        return context


class UserDetailView(PaginateMixin, ListView):

    template_name = "blog/profile.html"
    slug_url_kwarg = "username"
    slug_field = "username"
    context_object_name = "profile"

    def get_queryset(self) -> QuerySet:
        return posts_selected_with_unpublished_and_future().filter(
            author=author_selected(self.kwargs["username"])
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["profile"] = author_selected(self.kwargs["username"])
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):

    form_class = UserUpdateForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:index")


class PostCreateView(LoginRequiredMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        if form.instance.pub_date < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostDetailView(DetailView):

    template_name = "blog/detail.html"

    def get_object(self, queryset=None) -> Post:
        object = get_object_or_404(
            Post.objects.select_related("category", "author", "location"),
            id=self.kwargs["post_id"],
        )
        if (
            self.request.user == object.author
            or object.pub_date <= timezone.now()
            and object.is_published
            and object.category.is_published
        ):
            return object
        raise Http404

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        return context


class PostUpdateView(DispatchPostMixin, LoginRequiredMixin, UpdateView):

    template_name = "blog/create.html"
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    slug_url_kwarg = None

    def get_success_url(self) -> str:
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
            return get_object_or_404(queryset,
                                     pk=self.kwargs.get(self.pk_url_kwarg))


class PostDeleteView(DispatchPostMixin,
                     LoginRequiredMixin,
                     DeleteView):

    model = Post
    template_name = "blog/create.html"
    success_url = '/'
    pk_url_kwarg = 'post_id'
    slug_url_kwarg = None

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset,
                                 pk=self.kwargs.get(self.pk_url_kwarg))


class CommentCreateView(LoginRequiredMixin, CreateView):

    model = Comment
    form_class = CommentForm
    template_name = "includes/comments.html"

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, id=self.kwargs["post_id"])
        return super().form_valid(form)


class CommentUpdateView(DispatchCommentMixin,
                        LoginRequiredMixin,
                        UpdateView):

    form_class = CommentForm
    template_name = "blog/comment.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment, id=self.kwargs["comment_pk"])

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})


class CommentDeleteView(DispatchCommentMixin,
                        LoginRequiredMixin,
                        DeleteView):

    template_name = "blog/comment.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Comment,
                                 id=self.kwargs["comment_pk"])

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"post_id": self.kwargs["post_id"]})

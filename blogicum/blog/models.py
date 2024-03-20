from django.db import models
from django.contrib.auth.models import User
from core.models import PublishedCreatedModel, BasicTitle


class Category(BasicTitle, PublishedCreatedModel):
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL;"
            + " разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Location(PublishedCreatedModel):
    name = models.CharField(
        max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


class Post(BasicTitle, PublishedCreatedModel):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем"
            " — можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Местоположение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория"
    )
    image = models.ImageField(
        "Изображение",
        upload_to="posts_images",
        blank=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"


class Comment(models.Model):
    text = models.TextField(
        max_length=256,
        verbose_name="Текст комментария")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Автор комментария"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

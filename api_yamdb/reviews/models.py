from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from api_yamdb.constants import (
    NAME_MAX_LENGTH,
    REVIEW_SCORE_MAX,
    REVIEW_SCORE_MIN,
)
from reviews.services import current_year


class NamedSlugModel(models.Model):
    """Абстрактная модель: name + slug, общий str и ordering."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGTH)
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self) -> str:
        return str(self.name)


class Category(NamedSlugModel):
    """Категория произведений (например: книги, музыка, фильмы)."""

    class Meta(NamedSlugModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(NamedSlugModel):
    """Жанр произведений (например: драма, детектив, рок)."""

    class Meta(NamedSlugModel.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    """Произведение (title) в каталоге YaMDb."""

    name = models.CharField("Название", max_length=NAME_MAX_LENGTH)
    year = models.SmallIntegerField(
        "Год выпуска",
        validators=[MaxValueValidator(current_year)],
    )
    description = models.TextField("Описание", blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория",
    )

    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        related_name="titles",
        verbose_name="Жанры",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ("name",)

    def __str__(self) -> str:
        return str(self.name)


class GenreTitle(models.Model):
    """Связь many-to-many между Title и Genre."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="genre_titles",
        verbose_name="Произведение",
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name="genre_titles",
        verbose_name="Жанр",
    )

    class Meta:
        verbose_name = "Жанр произведения"
        verbose_name_plural = "Жанры произведений"
        constraints = [
            models.UniqueConstraint(
                fields=("title", "genre"),
                name="unique_title_genre",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title_id} <-> {self.genre_id}"


class TextWithPubDateModel(models.Model):
    """Абстрактная модель: текст + автор + дата публикации."""

    text = models.TextField("Текст")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    pub_date = models.DateTimeField(
        "Дата публикации",
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ("-pub_date",)


class Review(TextWithPubDateModel):
    """Отзыв пользователя на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )

    score = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[
            MinValueValidator(REVIEW_SCORE_MIN),
            MaxValueValidator(REVIEW_SCORE_MAX),
        ],
    )

    class Meta(TextWithPubDateModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        default_related_name = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=("title", "author"),
                name="unique_review_per_title_author",
            )
        ]

    def __str__(self) -> str:
        return f"Отзыв {self.author} к '{self.title}' ({self.score})"


class Comment(TextWithPubDateModel):
    """Комментарий пользователя к отзыву (Review)."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )

    class Meta(TextWithPubDateModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = "comments"

    def __str__(self) -> str:
        return f"Комментарий {self.author} к отзыву {self.review_id}"

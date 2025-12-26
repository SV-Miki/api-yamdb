from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def current_year() -> int:
    """Возвращает текущий год

    (используется валидатором поля year у произведений).
    """
    return timezone.now().year


class Category(models.Model):
    """Категория произведений (например: книги, музыка, фильмы)."""

    name = models.CharField("Название", max_length=256)
    slug = models.SlugField("Слаг", max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self) -> str:
        return str(self.name)


class Genre(models.Model):
    """Жанр произведений (например: драма, детектив, рок)."""

    name = models.CharField("Название", max_length=256)
    slug = models.SlugField("Слаг", max_length=50, unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("name",)

    def __str__(self) -> str:
        return str(self.name)


class Title(models.Model):
    """Произведение (title) в каталоге YaMDb.

    Связано с:
    - Category (FK, SET_NULL)
    - Genre (M2M через GenreTitle)
    """

    name = models.CharField("Название", max_length=256)
    year = models.PositiveSmallIntegerField(
        "Год выпуска",
        validators=[MaxValueValidator(current_year)],
    )
    description = models.TextField("Описание", blank=True)

    # При удалении категории произведения НЕ удаляются → SET_NULL
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория",
    )

    # При удалении жанра произведения НЕ удаляются → M2M просто очистит связь
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
        related_name="genre_links",
        verbose_name="Произведение",
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name="title_links",
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


class Review(models.Model):
    """Отзыв пользователя на произведение.

    Ограничение:
    один пользователь может оставить только один отзыв на одно произведение.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    text = models.TextField("Текст")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    score = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-pub_date",)
        constraints = [
            # “На одно произведение пользователь
            # может оставить только один отзыв”
            models.UniqueConstraint(
                fields=("title", "author"),
                name="unique_review_per_title_author",
            )
        ]

    def __str__(self) -> str:
        return f"Отзыв {self.author} к '{self.title}' ({self.score})"


class Comment(models.Model):
    """Комментарий пользователя к отзыву (Review)."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    text = models.TextField("Текст")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return f"Комментарий {self.author} к отзыву {self.review_id}"

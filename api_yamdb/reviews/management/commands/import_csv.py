import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

DATA_DIR = Path(settings.BASE_DIR) / "static" / "data"


def _read_csv(filename: str):
    """Читает CSV из каталога DATA_DIR и отдаёт строки как dict."""

    path = DATA_DIR / filename
    with path.open(encoding="utf-8") as f:
        yield from csv.DictReader(f)


class Command(BaseCommand):
    """Импорт данных YaMDb из CSV-файлов каталога DATA_DIR.

    Команда идемпотентна:
    использует update_or_create и может запускаться повторно.
    Импорт выполняется в одной транзакции.
    """

    help = "Import YaMDb data from CSV files located in DATA_DIR"

    @transaction.atomic
    def handle(self, *args, **options):
        """Точка входа команды: выполняет импорт шагов по порядку."""
        self.stdout.write(self.style.WARNING(f"DATA_DIR = {DATA_DIR}"))

        steps = (
            ("users.csv", self._import_users),
            ("category.csv", self._import_categories),
            ("genre.csv", self._import_genres),
            ("titles.csv", self._import_titles),
            ("genre_title.csv", self._import_genre_title),
            ("review.csv", self._import_reviews),
            ("comments.csv", self._import_comments),
        )

        for filename, func in steps:
            func(filename)

        self.stdout.write(self.style.SUCCESS("Import finished"))

    def _import_users(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            User.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "username": row["username"],
                    "email": row["email"],
                    "role": row.get("role", "user"),
                    "bio": row.get("bio", ""),
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"users: {count}"))

    def _import_categories(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            Category.objects.update_or_create(
                id=int(row["id"]),
                defaults={"name": row["name"], "slug": row["slug"]},
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"categories: {count}"))

    def _import_genres(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            Genre.objects.update_or_create(
                id=int(row["id"]),
                defaults={"name": row["name"], "slug": row["slug"]},
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"genres: {count}"))

    def _import_titles(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            Title.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "name": row["name"],
                    "year": int(row["year"]),
                    "category_id": int(row["category"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"titles: {count}"))

    def _import_genre_title(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            GenreTitle.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "title_id": int(row["title_id"]),
                    "genre_id": int(row["genre_id"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"genre_title: {count}"))

    def _import_reviews(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            Review.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "title_id": int(row["title_id"]),
                    "text": row["text"],
                    "author_id": int(row["author"]),
                    "score": int(row["score"]),
                    "pub_date": row["pub_date"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"reviews: {count}"))

    def _import_comments(self, filename: str):
        count = 0
        for row in _read_csv(filename):
            Comment.objects.update_or_create(
                id=int(row["id"]),
                defaults={
                    "review_id": int(row["review_id"]),
                    "text": row["text"],
                    "author_id": int(row["author"]),
                    "pub_date": row["pub_date"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"comments: {count}"))

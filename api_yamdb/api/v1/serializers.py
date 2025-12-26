from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


SLUG_REGEX = r"^[-a-zA-Z0-9_]+$"
slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message="Slug может содержать только латинские буквы, "
            "цифры, дефис и подчёркивание.",
)


class SignupSerializer(serializers.Serializer):
    """Данные для регистрации: username + email (с запретом username='me')."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )

    def validate_username(self, value: str) -> str:
        if value.lower() == "me":
            raise serializers.ValidationError(
                "Использовать username='me' запрещено."
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Данные для получения JWT: username + confirmation_code."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для админского CRUD (/users/)."""

    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value: str) -> str:
        if value.lower() == "me":
            raise serializers.ValidationError(
                "Использовать username='me' запрещено."
            )
        return value

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "bio", "role"
        )


class UserMeSerializer(UserSerializer):
    """Для /users/me/: роль менять нельзя."""

    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории (name, slug)."""

    slug = serializers.CharField(
        max_length=50,
        validators=[
            slug_validator,
            UniqueValidator(queryset=Category.objects.all()),
        ],
    )

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра (name, slug)."""

    slug = serializers.CharField(
        max_length=50,
        validators=[
            slug_validator,
            UniqueValidator(queryset=Genre.objects.all()),
        ],
    )

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведения для чтения

    (вложенные category/genre + rating).
    """

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id", "name", "year", "rating", "description", "genre", "category"
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор произведения для записи (category/genre по slug)."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all(),
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = ("name", "year", "description", "genre", "category")

    def to_representation(self, instance):
        instance = (
            Title.objects.select_related("category")
            .prefetch_related("genre")
            .annotate(rating=Cast(Avg("reviews__score"), IntegerField()))
            .get(pk=instance.pk)
        )
        return TitleReadSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва: текст, оценка, автор (username),

    дата публикации.
    """

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, attrs):
        request = self.context["request"]
        if request.method == "POST":
            title_id = self.context["view"].kwargs["title_id"]
            if Review.objects.filter(
                    title_id=title_id, author=request.user
            ).exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "Вы уже оставляли отзыв на это произведение."
                        ]
                    }
                )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария: текст, автор (username), дата публикации."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")

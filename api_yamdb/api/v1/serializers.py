from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api_yamdb.constants import (
    EMAIL_MAX_LENGTH,
    RESERVED_USERNAME,
    USERNAME_MAX_LENGTH,
    REVIEW_SCORE_MIN,
    REVIEW_SCORE_MAX,
    SLUG_REGEX,
    SLUG_MAX_LENGTH,
)

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

slug_validator = RegexValidator(
    regex=SLUG_REGEX,
    message="Slug может содержать только латинские буквы, "
            "цифры, дефис и подчёркивание.",
)


class SignupSerializer(serializers.Serializer):
    """Данные для регистрации пользователя (username и email)."""

    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[UnicodeUsernameValidator()],
    )

    def validate(self, attrs):
        username = attrs["username"]
        email = attrs["email"]

        if username == RESERVED_USERNAME:
            raise serializers.ValidationError(
                {"username": [
                    f'Нельзя использовать username "{RESERVED_USERNAME}".'
                ]}
            )

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        errors = {}
        if user_by_username and user_by_username.email != email:
            errors["username"] = ["Этот username уже занят другим email."]
        if user_by_email and user_by_email.username != username:
            errors["email"] = ["Этот email уже занят другим username."]

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class TokenSerializer(serializers.Serializer):
    """Данные для получения JWT: username + confirmation_code."""

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        username = attrs["username"]
        code = attrs["confirmation_code"]

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, code):
            raise serializers.ValidationError(
                {"confirmation_code": ["Неверный код подтверждения."]}
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Пользователь (CRUD админом + используется во viewset users)."""

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "bio", "role"
        )
        extra_kwargs = {
            "email": {"max_length": EMAIL_MAX_LENGTH},
        }


class UserMeSerializer(UserSerializer):
    """Профиль текущего пользователя (/users/me/): роль менять нельзя."""

    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Категория: name, slug."""

    class Meta:
        model = Category
        fields = ("name", "slug")
        extra_kwargs = {
            "slug": {
                "max_length": SLUG_MAX_LENGTH,
                "validators": [
                    slug_validator,
                    UniqueValidator(queryset=Category.objects.all()),
                ],
            }
        }


class GenreSerializer(serializers.ModelSerializer):
    """Жанр: name, slug."""

    class Meta:
        model = Genre
        fields = ("name", "slug")
        extra_kwargs = {
            "slug": {
                "max_length": SLUG_MAX_LENGTH,
                "validators": [
                    slug_validator,
                    UniqueValidator(queryset=Genre.objects.all()),
                ],
            }
        }


class TitleReadSerializer(serializers.ModelSerializer):
    """Произведение для чтения: category/genre вложенно + rating."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id", "name", "year", "rating", "description", "genre", "category"
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Произведение для записи: category/genre по slug."""

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
    """Отзыв: text, score, author, pub_date."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )
    score = serializers.IntegerField(
        min_value=REVIEW_SCORE_MIN, max_value=REVIEW_SCORE_MAX
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, attrs):
        request = self.context.get("request")
        view = self.context.get("view")
        if request and view and request.method == "POST":
            title_id = view.kwargs.get("title_id")
            if Review.objects.filter(
                    title_id=title_id, author=request.user
            ).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": [
                        "Вы уже оставляли отзыв на это произведение."
                    ]}
                )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Комментарий: text, author, pub_date."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")

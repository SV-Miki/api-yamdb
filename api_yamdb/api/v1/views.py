from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.pagination import DefaultPagination
from api.v1.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly,
)
from api.v1.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignupView(APIView):
    """Регистрация пользователя: создаёт/переиспользует пользователя

    и отправляет confirmation_code на email.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]

        # Если пользователь уже есть
        # - проверяем согласованность username/email.
        user_by_username = User.objects.filter(
            username=username
        ).first()
        user_by_email = User.objects.filter(email=email).first()

        errors = {}

        if user_by_username and user_by_username.email != email:
            errors["username"] = ["Этот username уже занят другим email."]

        if user_by_email and user_by_email.username != username:
            errors["email"] = ["Этот email уже занят другим username."]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(username=username, email=email)

        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject="YaMDb confirmation code",
            message=f"Ваш код подтверждения: {confirmation_code}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"email": email, "username": username}, status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """Выдаёт JWT-токен по username и confirmation_code."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        code = serializer.validated_data["confirmation_code"]

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, code):
            return Response(
                {"confirmation_code": ["Неверный код подтверждения."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access = RefreshToken.for_user(user).access_token
        return Response({"token": str(access)}, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """Админский CRUD пользователей

    + эндпоинт /users/me/ для текущего пользователя.
    """

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    lookup_field = "username"
    filter_backends = (SearchFilter,)
    search_fields = ("username",)

    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_permissions(self):
        if getattr(self, "action", None) == "me":
            return [IsAuthenticated()]
        return [IsAdmin()]

    @action(detail=False, methods=("get", "patch", "delete"), url_path="me")
    def me(self, request):
        user = request.user

        if request.method == "GET":
            return Response(UserMeSerializer(user).data)

        if request.method == "PATCH":
            serializer = UserMeSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Категории: список/создание/удаление. Запись доступна только админу."""

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    http_method_names = ["get", "post", "delete", "head", "options"]


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Жанры: список/создание/удаление. Запись доступна только админу."""

    queryset = Genre.objects.all().order_by("name")
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    http_method_names = ["get", "post", "delete", "head", "options"]


class TitleViewSet(viewsets.ModelViewSet):
    """Произведения: CRUD с фильтрацией по category/genre/name/year

    и расчётом rating.
    """

    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = (
            Title.objects.all()
            .select_related("category")
            .prefetch_related("genre")
            .annotate(rating=Cast(Avg("reviews__score"), IntegerField()))
            .order_by("id")
        )

        params = self.request.query_params

        category = params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        genre = params.get("genre")
        if genre:
            qs = qs.filter(genre__slug=genre)

        name = params.get("name")
        if name:
            qs = qs.filter(name__icontains=name)

        year = params.get("year")
        if year:
            qs = qs.filter(year=year)

        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы к произведению (вложенный ресурс titles/{title_id}/reviews/)."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        title_id = self.kwargs["title_id"]
        return (
            Review.objects.filter(title_id=title_id)
            .select_related("author", "title")
            .order_by("id")
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзыву

    (вложенный ресурс titles/{title_id}/reviews/{review_id}/comments/).
    """

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        title_id = self.kwargs["title_id"]
        review_id = self.kwargs["review_id"]
        return (
            Comment.objects.filter(
                review_id=review_id, review__title_id=title_id
            )
            .select_related("author", "review")
            .order_by("id")
        )

    def perform_create(self, serializer):
        title_id = self.kwargs["title_id"]
        review_id = self.kwargs["review_id"]
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)

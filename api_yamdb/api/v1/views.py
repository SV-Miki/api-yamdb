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
    SignupSerializer,
    TokenSerializer,
    UserSerializer,
    UserMeSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
)

User = get_user_model()


class SignupView(APIView):
    """Регистрация пользователя и отправка confirmation_code на email."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]

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

        user = serializer.validated_data["user"]
        access = RefreshToken.for_user(user).access_token
        return Response({"token": str(access)}, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """Админский CRUD пользователей + /users/me/ для текущего пользователя."""

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    lookup_field = "username"
    filter_backends = (SearchFilter,)
    search_fields = ("username",)

    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_permissions(self):
        if getattr(self, "action", None) == "me":
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if getattr(self, "action", None) == "me":
            return UserMeSerializer
        return UserSerializer

    @action(detail=False, methods=("get", "patch", "delete"), url_path="me")
    def me(self, request):
        if request.method == "DELETE":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        user = request.user

        if request.method == "GET":
            return Response(self.get_serializer(user).data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Категории: список/создание/удаление. Изменения - только админу."""

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
    """Жанры: список/создание/удаление. Изменения - только админу."""

    queryset = Genre.objects.all().order_by("name")
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    http_method_names = ["get", "post", "delete", "head", "options"]


class TitleViewSet(viewsets.ModelViewSet):
    """Произведения: CRUD + фильтрация + rating."""

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
    """Отзывы к произведению."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.select_related("author", "title").order_by("id")

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзыву."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_review(self):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        return get_object_or_404(
            Review, id=self.kwargs["review_id"], title=title
        )

    def get_queryset(self):
        review = self.get_review()
        return review.comments.select_related(
            "author", "review"
        ).order_by("id")

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

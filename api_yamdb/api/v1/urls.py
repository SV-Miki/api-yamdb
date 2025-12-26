from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenView,
    UsersViewSet,
)

router = DefaultRouter()
router.register("users", UsersViewSet, basename="users")
router.register("categories", CategoryViewSet, basename="categories")
router.register("genres", GenreViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")

review_list = ReviewViewSet.as_view({"get": "list", "post": "create"})
review_detail = ReviewViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

comment_list = CommentViewSet.as_view({"get": "list", "post": "create"})
comment_detail = CommentViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("auth/signup/", SignupView.as_view(), name="auth-signup"),
    path("auth/token/", TokenView.as_view(), name="auth-token"),
    # reviews
    path("titles/<int:title_id>/reviews/", review_list, name="review-list"),
    path(
        "titles/<int:title_id>/reviews/<int:pk>/",
        review_detail, name="review-detail"
    ),
    # comments
    path(
        "titles/<int:title_id>/reviews/<int:review_id>/comments/",
        comment_list,
        name="comment-list",
    ),
    path(
        "titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/",
        comment_detail,
        name="comment-detail",
    ),
    path("", include(router.urls)),
]

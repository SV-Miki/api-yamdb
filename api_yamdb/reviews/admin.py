from django.contrib import admin

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)


class GenreTitleInline(admin.TabularInline):
    model = GenreTitle
    extra = 0


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "category")
    list_filter = ("category", "year")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (GenreTitleInline,)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "score", "pub_date")
    list_filter = ("score", "pub_date")
    search_fields = ("text", "author__username", "title__name")
    ordering = ("-pub_date",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "author", "pub_date")
    list_filter = ("pub_date",)
    search_fields = ("text", "author__username")
    ordering = ("-pub_date",)

from django.contrib import admin

from blog.models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """ Административная панель таблицы статей """
    list_display = ['author', 'title', 'text', 'is_active']
    search_fields = ['author', 'title']
    list_filter = ['author', 'is_active']

    list_per_page = 1000


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """ Административная панель таблицы комментариев """
    list_display = ['article', 'user', 'text']
    search_fields = ['user']
    list_filter = ['user']

    list_per_page = 1000

from django.contrib import admin

from blog.models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """ Административная панель таблицы статей """
    list_display = ['author', 'id', 'title', 'piece_text', 'is_active']
    search_fields = ['author', 'title']
    list_filter = ['author', 'is_active']

    list_per_page = 1000


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """ Административная панель таблицы комментариев """
    list_display = ['user', 'id', 'piece_text', 'article']
    search_fields = ['user']
    list_filter = ['user']

    list_per_page = 1000

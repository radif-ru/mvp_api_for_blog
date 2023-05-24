from django.contrib import admin

from users.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """ Административная панель таблицы токенов """
    list_display = ['user', 'token', 'is_active']
    search_fields = ['user']
    list_filter = ['user', 'is_active']

    list_per_page = 1000

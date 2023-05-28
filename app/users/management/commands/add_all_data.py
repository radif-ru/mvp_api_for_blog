import os

from django.core.management.base import BaseCommand

from utils.json import load_from_json
from .add_user import Command as AddUser
from blog.management.commands.add_article import Command as AddArticle
from blog.management.commands.add_comment import Command as AddComment


class Command(BaseCommand):
    help = 'Подготовка и выполнение миграций. ' \
           'Сборка стандартных и подготовленных статических файлов. ' \
           'Сборка всех подготовленных данных в БД, для таблиц ' \
           '`users`, `articles`, `comments` из файлов, ' \
           'которые хранятся в `./app/files/json`. ' \
           'К создаваемым пользователям рандомно прикрепляются статьи, ' \
           'а к статьям генерируются рандомные комментарии ' \
           'с рандомными авторами, данные связываются только с существующими.'

    def handle(self, *args, **options):
        """ Подготовка и выполнение миграций.
        Сборка стандартных и подготовленных статических файлов.
        Сборка всех подготовленных данных в БД,
        для таблиц `users`, `articles`, `comments` из файлов,
        которые хранятся в `./app/files/json`,
        данные связываются только с существующими.
        """
        self.migrate()
        self.collect_static()

        users = load_from_json('users')
        for user in users:
            AddUser.create_user(username=user['username'],
                                password=user['password'],
                                is_superuser=user['is_superuser'])

        articles = load_from_json('articles')
        for article in articles:
            AddArticle.add_article(title=article['title'],
                                   text=article['text'])

        comments = load_from_json('comments')
        for comment in comments:
            AddComment.add_comment(text=comment['text'])

    @staticmethod
    def migrate():
        """ Подготовка и выполнение миграций """
        os.system('python manage.py makemigrations --noinput')
        os.system('python manage.py migrate --noinput')

    @staticmethod
    def collect_static():
        """ Сборка стандартных и подготовленных статических файлов """
        os.system('mkdir static')
        os.system('python manage.py collectstatic --no-input --clear')

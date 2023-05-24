import os

from django.core.management.base import BaseCommand

from blog.utils import load_from_json
from .add_users import Command as AddUsers
from blog.management.commands.add_article import Command as AddArticles
from blog.management.commands.add_comment import Command as AddComments


class Command(BaseCommand):
    help = 'Сборка всех подготовленных данных'

    def handle(self, *args, **options):
        self.migrate()
        self.collect_static()

        users = load_from_json('users')
        for user in users:
            AddUsers.create_user(username=user['username'],
                                 password=user['password'],
                                 is_superuser=user['is_superuser'])

        articles = load_from_json('articles')
        for article in articles:
            AddArticles.add_article(title=article['title'],
                                    text=article['text'])

        comments = load_from_json('comments')
        for comment in comments:
            AddComments.add_comment(text=comment['text'])

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

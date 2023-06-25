import json

from django.contrib.auth.models import User
from django.test import TestCase
from mixer.backend.django import mixer

from blog.models import Article, Comment
from config.settings import RESPONSE_MESSAGES
from users.models import Token
from utils.token import gen_token


class ArticleViewTestCase(TestCase):
    def setUp(self) -> None:
        self.endpoint = '/api/articles/'

        self.auth_user = mixer.blend(User, is_superuser=False)
        self.auth_superuser = mixer.blend(User, is_superuser=True)
        self.no_auth_user = mixer.blend(User)

        # Пример активного токена пользователя
        self.auth_user_token = mixer.blend(Token, user_id=self.auth_user.id,
                                           is_active=True, token=gen_token(32))
        # Пример активного токена админа
        self.auth_superuser_token = mixer.blend(
            Token,
            user_id=self.auth_superuser.id,
            is_active=True,
            token=gen_token(32))
        # Пример удалённого (архивного) токена
        self.no_auth_user_token = mixer.blend(Token,
                                              user_id=self.no_auth_user.id,
                                              is_active=False,
                                              token=gen_token(32))

        # Статья привязывается к пользователю с активным токеном
        self.article = mixer.blend(Article, author_id=self.auth_user.id)
        self.article_2 = mixer.blend(Article, author_id=self.auth_user.id)

        self.comment_1 = mixer.blend(Comment, user_id=self.auth_user.id,
                                     article_id=self.article.id)
        self.comment_2 = mixer.blend(Comment, user_id=self.auth_user.id,
                                     article_id=self.article.id)
        self.comment_3 = mixer.blend(Comment, user_id=self.auth_user.id,
                                     article_id=self.article.id)

        self.new_comment_title = 'Попутный ветер'
        self.new_comment_text = 'Много важного текста...'
        self.correct_post_data = {'title': self.new_comment_title,
                                  'text': self.new_comment_text}
        # Пример когда не хватает 1 из обязательных полей:
        self.incorrect_post_data_1 = {'title': self.new_comment_title}
        self.incorrect_post_data_2 = {'text': self.new_comment_text}

        self.content_type = 'application/json'

    def test_get(self):
        """ Тестирование GET запросов """
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'{self.endpoint}?id={self.article.id}')
        self.assertEqual(response.status_code, 200)

        # Вывод статьи и комментариев к ней по несуществующему id
        response = self.client.get(f'{self.endpoint}?id=999999999')
        self.assertEqual(response.status_code, 404)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_found}
        self.assertEqual(json.loads(response.content), message)

    def test_post(self):
        """ Тестирование POST запросов """
        # Неавторизованный пользователь делает post запрос
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.no_token}
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос, но токен не действителен
        response = self.client.post(
            self.endpoint,
            headers={'Authorization': self.no_auth_user_token.token},
            data=self.correct_post_data,
            content_type=self.content_type)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_valid_token}
        self.assertEqual(json.loads(response.content), message)

        # Не хватает обязательного поля text
        response = self.client.post(
            self.endpoint,
            headers={
                'Authorization': self.auth_user_token.token},
            data=self.incorrect_post_data_1,
            content_type=self.content_type)
        self.assertEqual(response.status_code, 400)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.no_required_fields}
        self.assertEqual(json.loads(response.content), message)

        # Не хватает обязательного поля title
        response = self.client.post(
            self.endpoint,
            headers={'Authorization': self.auth_user_token.token},
            data=self.incorrect_post_data_2,
            content_type=self.content_type)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос
        response = self.client.post(
            self.endpoint,
            headers={
                'Authorization': self.auth_user_token.token},
            data=self.correct_post_data,
            content_type=self.content_type)
        self.assertEqual(response.status_code, 201)
        # Проверяю, что вернулся article_id
        self.assertEqual('article_id' in json.loads(response.content), True)
        # Проверяю корректность ответа
        self.assertEqual(json.loads(response.content)['status'],
                         RESPONSE_MESSAGES.success)

    def test_patch(self):
        """ Тестирование PATCH запросов """
        # Неавторизованный пользователь делает patch запрос
        response = self.client.patch(self.endpoint)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.no_token}
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос, но токен не действителен
        response = self.client.patch(
            self.endpoint,
            headers={'Authorization': self.no_auth_user_token.token},
            data={'id': self.article.id, 'text': 'Абракадабра'},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_valid_token}
        self.assertEqual(json.loads(response.content), message)

        # Передаю id не существующего (или архивного) комментария
        response = self.client.patch(
            self.endpoint,
            headers={'Authorization': self.auth_user_token.token},
            data={'id': 9999999, 'text': 'Вот как то так'},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 404)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_found}
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос
        response = self.client.patch(
            self.endpoint,
            headers={'Authorization': self.auth_user_token.token},
            data={'id': self.article.id, 'title': 'Абракадабра'},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 204)

    def test_delete(self):
        """ Тестирование DELETE запросов """
        # Неавторизованный пользователь делает delete запрос
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.no_token}
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос, но токен не действителен
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.no_auth_user_token.token},
            data={'id': self.article_2.id},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 401)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_valid_token}
        self.assertEqual(json.loads(response.content), message)

        # Передаю id не существующего (или архивного) комментария
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.auth_user_token.token},
            data={'id': 9999999},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 404)
        message = {'status': RESPONSE_MESSAGES.no_success,
                   'error': RESPONSE_MESSAGES.not_found}
        self.assertEqual(json.loads(response.content), message)

        # Корректный запрос
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.auth_user_token.token},
            data={'id': self.article_2.id},
            content_type=self.content_type)
        self.assertEqual(response.status_code, 204)

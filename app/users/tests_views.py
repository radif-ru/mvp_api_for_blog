import json

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from mixer.backend.django import mixer

from config.settings import RESPONSE_MESSAGES
from users.models import Token


class TokenViewTestCase(TestCase):
    def setUp(self) -> None:
        self.endpoint = '/api/token/'

        self.user_password = 'superP@55'
        self.user_password_hash = make_password(password=self.user_password)
        self.user_1 = mixer.blend(User,
                                  password=self.user_password_hash,
                                  is_active=True)
        self.user_token_1 = mixer.blend(Token, user=self.user_1)
        self.user_2 = mixer.blend(User)
        self.user_token_2 = mixer.blend(Token, user=self.user_2)
        self.user_3 = mixer.blend(User)
        self.user_token_3 = mixer.blend(Token, user=self.user_3)
        self.superuser = mixer.blend(User,
                                     is_superuser=True,
                                     password=self.user_password_hash,
                                     is_active=True)
        self.superuser_token = mixer.blend(Token, user=self.superuser)

        self.content_type = 'application/json'

    def test_post(self):
        """ Тестирование POST запросов """
        # Корректный запрос для создания токена
        response = self.client.post(
            self.endpoint,
            data={'username': self.user_1.username,
                  'password': self.user_password},
            content_type=self.content_type)

        # Проверяю корректность ответа на запрос создания токена в БД
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content)
        response_id = response_data['id']
        response_status = response_data['status']
        response_token = response_data['token']

        # Проверяю удачно ли прошёл запрос
        self.assertEqual(response_status, RESPONSE_MESSAGES.success)

        token_obj = Token.objects.filter(id=response_id).first()

        # Сравниваю токен из response с токеном созданными в БД
        self.assertEqual(token_obj.token, response_token)

        # Не корректный запрос
        response = self.client.post(
            self.endpoint,
            data={'username': self.user_1.username},
            content_type=self.content_type)

        # Проверяю корректность ответа на запрос создания токена в БД,
        # но с недостающим полем "password"
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.content)
        response_status = response_data['status']
        response_error = response_data['error']

        # Проверяю корректность поля status в response
        self.assertEqual(response_status, RESPONSE_MESSAGES.no_success)
        # Проверяю корректность ошибки, указывающей на недостающее поле
        self.assertEqual(response_error, RESPONSE_MESSAGES.no_required_fields)

    def test_delete(self):
        """ Тестирование DELETE запросов """
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.user_token_1.token},
            content_type=self.content_type)

        # Проверяю корректность ответа на запрос удаления токена из БД
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.user_token_1.token},
            content_type=self.content_type)

        # Проверяю корректность ответа на запрос удаления токена из БД в случае
        # если токен не активен
        self.assertEqual(response.status_code, 401)

        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': 'Не корректный токен!'},
            content_type=self.content_type)

        # Проверяю корректность ответа на запрос удаления токена из БД в случае
        # если токен не действителен или отсутствует
        self.assertEqual(response.status_code, 401)

        # Проверяю возможность админа удалить чужой токен по id
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.superuser_token.token},
            data={'id': self.user_token_2.id},
            content_type=self.content_type)

        self.assertEqual(response.status_code, 204)

        # Проверяю возможность админа удалить чужой токен по его содержимому
        response = self.client.delete(
            self.endpoint,
            headers={'Authorization': self.superuser_token},
            data={'id': self.user_token_3.token},
            content_type=self.content_type)

        self.assertEqual(response.status_code, 204)

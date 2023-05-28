from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View

from config.settings import RESPONSE_MESSAGES
from decorators.auth import auth_with_token
from decorators.request import json_request
from users.models import Token
from utils.token import gen_token


class TokenView(View):

    @json_request
    def post(self, request, data, message, *args, **kwargs):
        """ Создать токен.
        Генерирует новый токен, в теле запроса (`JSON`-формат) необходимо
        передать `username` и `password`.
        В случае успешной идентификации пользователя
        возвращает сообщение с результатом, сгенерированный token` и его `id`.
        В случае ошибки возвращает её описание.
        """

        username: str = data['username'] if data.get('username') else ''
        password: str = data['password'] if data.get('password') else ''

        if not username:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            return JsonResponse(data=message, status=400)
        if not password:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            return JsonResponse(data=message, status=400)

        user: User = User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                token: str = gen_token(32)
                token_obj: Token = Token.objects.create(user_id=user.id,
                                                        token=token)
                message['token']: str = token_obj.token
                message['id']: str = token_obj.id
                return JsonResponse(data=message, status=201)
            else:
                message['status']: str = RESPONSE_MESSAGES.no_success
                message['error']: str = RESPONSE_MESSAGES.incorrect_data
                return JsonResponse(data=message, status=401)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return JsonResponse(data=message, status=401)

    @auth_with_token
    @json_request
    def delete(self, request, data, message, *args, **kwargs):
        """ Удалить токен (перенести в архив).
        Токен должен быть указан в заголовке (`headers`) `Authorization`.
        Обычному пользователю можно удалить только
        текущий токен - по которому он аутентифицируется.
        Админ может удалить любой токен, для этого нужно
        передать в теле запроса (`JSON`-формат)
        `token` (токен) или `id` (идентификатор).
        Возвращает результат выполнения и описание ошибки (если есть).
        """
        user: User = request.user
        token_id: int = data.get('id', 0)
        token_content: str = data.get('token', '')

        if token_id and user.is_superuser:
            token: Token or None = Token.objects.filter(
                id=token_id, is_active=True).first()
        elif token_content and user.is_superuser:
            token: Token or None = Token.objects.filter(
                token=token_content, is_active=True).first()
        else:
            token: Token or None = Token.objects.filter(
                user_id=user.id, token=request.headers.get('Authorization')
            ).first()

        if token:
            token.delete()
            return JsonResponse(data=message, status=204)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return JsonResponse(data=message, status=401)

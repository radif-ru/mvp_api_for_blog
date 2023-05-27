from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from config.settings import RESPONSE_MESSAGES
from decorators.auth import user_auth_with_token
from mixins.view import ViewParseRequestBodyMixin
from users.models import Token
from utils.response import get_response_serialized_in_json
from utils.token import gen_token


class TokenView(ViewParseRequestBodyMixin, View):

    def post(self, request, *args, **kwargs):
        """ Создать токен.
        Генерирует новый токен, в теле запроса необходимо
        передать `username` и `password`.
        В случае успешной идентификации пользователя
        возвращает сообщение с результатом, сгенерированный token` и его `id`.
        В случае ошибки возвращает её описание.
        """

        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        message: dict = {'status': RESPONSE_MESSAGES.success}

        if not username:
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response
        if not password:
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response

        user: User = User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                token: str = gen_token(32)
                token_obj: Token = Token.objects.create(user_id=user.id,
                                                        token=token)
                message['token']: str = token_obj.token
                message['id']: str = token_obj.id
                response: HttpResponse = get_response_serialized_in_json(
                    content=message, status=201)
                return response
            else:
                message['error']: str = RESPONSE_MESSAGES.incorrect_data
                response: HttpResponse = get_response_serialized_in_json(
                    content=message, status=401)
                return response
        else:
            message['error']: str = RESPONSE_MESSAGES.not_found

            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=401)
            return response

    @user_auth_with_token
    def delete(self, request, *args, **kwargs):
        """ Удалить токен (перенести в архив).
        Токен должен быть указан в заголовке (`headers`) `Authorization`.
        Обычному пользователю можно удалить только
        текущий токен - по которому он аутентифицируется.
        Админ может удалить любой токен, для этого нужно
        передать в теле запроса `token` (токен) или `id` (идентификатор).
        Возвращает результат выполнения и описание ошибки (если есть).
        """
        user: User = request.user
        body: list = self.parse_request_body()
        token_id: int = 0
        token_content: str = ''
        message: dict = {'status': RESPONSE_MESSAGES.success}
        for num, el in enumerate(body, start=0):
            if 'name="id"' in el:
                token_id: int = int(body[num + 2])
            if 'name="token"' in el:
                token_content: str = body[num + 2]

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
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=204)
            return response
        else:
            message['error']: str = RESPONSE_MESSAGES.not_found
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=401)
            return response

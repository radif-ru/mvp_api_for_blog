import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from users.decorators import user_auth_with_token
from blog.mixins import ViewParseRequestBodyMixin
from config.settings import RESPONSE_MESSAGES
from users.models import Token
from users.utils import gen_token


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
            return HttpResponse(content=json.dumps(message), status=400)
        if not password:
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            return HttpResponse(content=json.dumps(message), status=400)

        user: User = User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                token: str = gen_token(32)
                token_obj: Token = Token.objects.create(user_id=user.id,
                                                        token=token)

                message['token']: str = token_obj.token
                message['id']: str = token_obj.id
                return HttpResponse(content=json.dumps(message), status=201)
            else:
                message['error']: str = RESPONSE_MESSAGES.incorrect_data
                return HttpResponse(content=json.dumps(message), status=401)
        else:
            message['error']: str = RESPONSE_MESSAGES.not_found
            return HttpResponse(content=json.dumps(message), status=401)

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
            return HttpResponse(content=json.dumps(message), status=204)
        else:
            message['error']: str = RESPONSE_MESSAGES.not_found
            return HttpResponse(content=json.dumps(message), status=401)

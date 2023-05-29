from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse

from config.settings import RESPONSE_MESSAGES
from utils.response import get_response_serialized_in_json


def auth_with_token(function):
    """ Аутентификация пользователя по токену.
    В заголовке (`headers`) `Authorization`
    необходимо указать действительный токен.
    В случае ошибки возвращает её описание.
    """

    def wrapper(self, request, *args, **kwargs):

        token: str or None = request.headers.get('Authorization')
        message: dict = {'status': RESPONSE_MESSAGES.success}
        if not token:
            message['status'] = RESPONSE_MESSAGES.no_success
            message['error'] = RESPONSE_MESSAGES.no_token
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=401)
            return response
        user: User = User.objects.filter(token__token=token,
                                         token__is_active=True).first()

        if not user:
            message['status'] = RESPONSE_MESSAGES.no_success
            message['error'] = RESPONSE_MESSAGES.not_valid_token
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=401)
            return response

        login(request, user)

        result = function(self, request, *args, **kwargs)

        return result

    return wrapper

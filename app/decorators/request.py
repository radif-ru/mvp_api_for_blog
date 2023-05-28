import json
from json import JSONDecodeError

from django.http import JsonResponse

from config.settings import RESPONSE_MESSAGES


def json_request(function):
    """ Проверить соответствие отправляемых клиентом данных `JSON`-формату.
    При несоответствии клиенту возвращается сообщение об этом.
    Возвращает десериализованные данные `data`.
    """

    def wrap(self, request, *args, **kwargs):

        message: dict = {'status': RESPONSE_MESSAGES.success}
        try:
            data: dict = json.loads(request.body)
        except JSONDecodeError:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.json_error
            return JsonResponse(data=message, status=400)

        return function(self, request, data, message, *args, **kwargs)

    return wrap

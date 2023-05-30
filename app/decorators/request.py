import json
from json import JSONDecodeError
from typing import Iterable

from django.http import JsonResponse

from config.settings import RESPONSE_MESSAGES


def json_request(required_fields: Iterable or None = None):
    """ Проверить соответствие отправляемых клиентом данных `JSON`-формату.
    При несоответствии клиенту возвращается сообщение об этом.
    Возвращает десериализованные данные `data`.
    :param required_fields обязательные поля в теде
    """

    def decorator(function):
        def wrapper(self, request, *args, **kwargs):
            message: dict = {'status': RESPONSE_MESSAGES.success}
            try:
                data: dict = json.loads(request.body)
            except JSONDecodeError:
                message['status']: str = RESPONSE_MESSAGES.no_success
                message['error']: str = RESPONSE_MESSAGES.json_error
                return JsonResponse(data=message, status=400)

            if required_fields:
                for required_field in required_fields:
                    if required_field not in data:
                        message['status']: str = RESPONSE_MESSAGES.no_success
                        message['error']: str = RESPONSE_MESSAGES.no_required_fields
                        return JsonResponse(data=message, status=400)

            result = function(self, request, data, message, *args, **kwargs)

            return result

        return wrapper

    return decorator

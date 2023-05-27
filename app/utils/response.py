import json

from django.http import HttpResponse


def get_response_serialized_in_json(content: dict or list,
                                    status: int = 200) -> HttpResponse:
    """ Получить HttpResponse, с сериализованными данными в json формат.
    :param content данные, которые необходимо сериализовать
    :param status возвращаемый статус-код, по умолчанию 200
    :return возвращает подготовленный HttpResponse
    """
    json_content: str = json.dumps(content, ensure_ascii=False)
    return HttpResponse(content=json_content, status=status,
                        content_type='application/json')

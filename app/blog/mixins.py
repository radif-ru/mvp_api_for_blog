import json

from django.contrib.auth.models import User
from django.http import HttpResponse


class ViewCheckAuthorizationMixin:
    def check_authorization(self) -> HttpResponse or User:
        """ Проверить авторизацию """
        token: str = self.request.headers.get('Authorization')
        if not token:
            error: str = json.dumps({'error': 'no token'})
            return HttpResponse(content=error, status=401)
        user: User = User.objects.filter(token__token=token,
                                         token__is_active=True).first()
        if not user:
            error: str = json.dumps({'error': 'token is not valid'})
            return HttpResponse(content=error, status=401)

        return user


class ViewParseRequestBodyMixin:
    def parse_request_body(self) -> list:
        """ Распарсить тело запроса """
        body: list = self.request.body.decode('utf-8').split('\r\n')
        return body

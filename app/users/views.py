import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from blog.mixins import ViewCheckAuthorizationMixin, ViewParseRequestBodyMixin
from users.models import Token
from users.utils import gen_token


class TokenView(ViewCheckAuthorizationMixin, ViewParseRequestBodyMixin, View):

    def post(self, request, *args, **kwargs):
        """ Создать токен """

        username: str = request.POST.get('username')
        password: str = request.POST.get('password')

        if not username:
            error: str = json.dumps({'error': 'no username'})
            return HttpResponse(content=error, status=400)
        if not password:
            error: str = json.dumps({'error': 'no password'})
            return HttpResponse(content=error, status=400)

        user: User = User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                token: str = gen_token(32)
                token_gen_res: Token = Token.objects.create(user_id=user.id, token=token)

                message: str = json.dumps({'token': token_gen_res.token, 'id': token_gen_res.id})
                return HttpResponse(content=message, status=201)
            else:
                error: str = json.dumps({'error': 'incorrect password'})
                return HttpResponse(content=error, status=401)
        else:
            error: str = json.dumps({'error': 'user not found'})
            return HttpResponse(content=error, status=401)

    def delete(self, request, *args, **kwargs):
        """ Удалить токен (перенести в архив) """
        check_result: HttpResponse or User = self.check_authorization()
        if isinstance(check_result, HttpResponse):
            return check_result
        user: User = check_result

        body: list = self.parse_request_body()
        token_id: int = 0
        for num, el in enumerate(body, start=0):
            if 'name="id"' in el:
                token_id: int = body[num + 2]

        if token_id:
            token_id: int = int(token_id)
            token = Token.objects.filter(id=token_id,
                                         is_active=True)

            if (
                    token and token.first().user.id == token_id
            ) or user.is_superuser:
                token.update(is_active=False)
                return HttpResponse(status=204)

        else:
            error: str = json.dumps({'error': 'no token id'})
            return HttpResponse(content=error, status=400)

        error: str = json.dumps({'error': 'forbidden act'})
        return HttpResponse(content=error, status=400)

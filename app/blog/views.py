from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from config.settings import RESPONSE_MESSAGES
from decorators.auth import user_auth_with_token
from mixins.view import ViewParseRequestBodyMixin
from utils.response import get_response_serialized_in_json
from .models import Article, Comment


class ArticleView(ViewParseRequestBodyMixin,
                  View):

    def get(self, request, *args, **kwargs):
        """ Получить статьи.
        Все активные или при передаче параметра `id` - статью с комментариями
        по переданному идентификатору.
        """

        article_id: int = int(request.GET.get('id')) if request.GET.get(
            'id') else None
        if article_id:
            article: Article = Article.objects.filter(id=article_id).first()
            comments: list = list(
                Comment.objects.filter(article_id=article_id).values())
            data: dict = {'id': article.id,
                          'title': article.title,
                          'text': article.text,
                          'author': article.author.username,
                          'comments': comments}
            response: HttpResponse = get_response_serialized_in_json(
                content=data)
            return response

        articles: [Article] = Article.objects.filter(is_active=True)
        response: HttpResponse = get_response_serialized_in_json(
            content=list(articles.values()))
        return response

    @user_auth_with_token
    def post(self, request, *args, **kwargs):
        """ Создать статью.
        Обязательные поля в теле запроса: `title`, `text`.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        title: str = request.POST.get('title')
        text: str = request.POST.get('text')
        message: dict = {'status': RESPONSE_MESSAGES.success}

        if not title:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response
        if not text:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response

        article: Article = Article.objects.create(author_id=user.id,
                                                  title=title, text=text)
        message['article_id']: str = article.id
        response: HttpResponse = get_response_serialized_in_json(
            content=message, status=201)
        return response

    @user_auth_with_token
    def patch(self, request, *args, **kwargs):
        """ Редактировать статью.
        Обычному пользователю можно редактировать только свои статьи.
        Админу можно редактировать любые статьи.
        В теле запроса необходимо указать поле `id` и `title` или `text`.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        body: list = self.parse_request_body()
        data: dict = {}
        article_id: int = 0
        message: dict = {'status': RESPONSE_MESSAGES.success}
        for num, el in enumerate(body, start=0):
            if 'name="title"' in el:
                data['title'] = body[num + 2]
            elif 'name="text"' in el:
                data['text'] = body[num + 2]
            elif 'name="id"' in el:
                article_id: int = int(body[num + 2])
        if not article_id or ('title' not in data and 'text' not in data):
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response

        article: [Article] = Article.objects.filter(id=article_id,
                                                    is_active=True)
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=404)
            return response

        if (article.first().author.id == user.id) or user.is_superuser:
            article.update(**data)

            response: HttpResponse = get_response_serialized_in_json(
                content=message)
            return response
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act

            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=403)
            return response

    @user_auth_with_token
    def delete(self, request, *args, **kwargs):
        """ Удалить статью (перенести в архив).
        Обычному пользователю можно удалять только свои статьи.
        Админу можно удалять любые статьи.
        В теле запроса необходимо указать поле `id` - идентификатор статьи.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        body: list = self.parse_request_body()
        article_id: int = 0
        message: dict = {'status': RESPONSE_MESSAGES.success}
        for num, el in enumerate(body, start=0):
            if 'name="id"' in el:
                article_id: int = int(body[num + 2])

        if not article_id:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=400)
            return response

        article: Article or None = Article.objects.filter(
            id=article_id, is_active=True).first()
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=404)
            return response

        if (article.author.id == user.id) or user.is_superuser:
            article.delete()
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=204)
            return response
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act
            response: HttpResponse = get_response_serialized_in_json(
                content=message, status=403)
            return response

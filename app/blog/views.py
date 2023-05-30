from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View

from config.settings import RESPONSE_MESSAGES
from decorators.auth import auth_with_token
from decorators.request import json_request
from .models import Article


class ArticleView(View):

    def get(self, request, *args, **kwargs):
        """ Получить статьи.
        Все активные или при передаче параметра `id` - статью с комментариями
        по переданному идентификатору.
        """

        article_id: int = int(request.GET.get('id', 0))
        if article_id:
            article: Article or None = Article.objects.filter(
                id=article_id).first()
            if not article:
                message: dict = {'status': RESPONSE_MESSAGES.no_success,
                                 'error': RESPONSE_MESSAGES.not_found}
                return JsonResponse(data=message, status=404)
            comments: list = list(article.comment_set.all().values())
            data: dict = {'id': article.id,
                          'title': article.title,
                          'text': article.text,
                          'author': article.author.username,
                          'comments': comments}
            return JsonResponse(data=data,
                                json_dumps_params={'ensure_ascii': False})

        articles: [Article] = Article.objects.filter(is_active=True)
        return JsonResponse(data=list(articles.values()), safe=False,
                            json_dumps_params={'ensure_ascii': False})

    @auth_with_token
    @json_request(required_fields=('title', 'text'))
    def post(self, request, data: dict, message: dict, *args, **kwargs):
        """ Создать статью.
        Обязательные поля в теле запроса (`JSON`-формат): `title`, `text`.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        title: str = data['title']
        text: str = data['text']

        article: Article = Article.objects.create(author_id=user.id,
                                                  title=title, text=text)
        message['article_id']: str = article.id
        return JsonResponse(data=message, status=201)

    @auth_with_token
    @json_request(required_fields=('id',))
    def patch(self, request, data: dict, message: dict, *args, **kwargs):
        """ Редактировать статью.
        Обычному пользователю можно редактировать только свои статьи.
        Админу можно редактировать любые статьи.
        В теле запроса (`JSON`-формат)
        необходимо указать поле `id` и `title` или `text`.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        article_id: int = int(data.pop('id'))

        if 'title' not in data and 'text' not in data:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            return JsonResponse(data=message, status=400)

        article: [Article] = Article.objects.filter(id=article_id,
                                                    is_active=True)
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return JsonResponse(data=message, status=404)
        if (article.first().author.id == user.id) or user.is_superuser:
            article.update(**data)
            return JsonResponse(data=message, status=204)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act
            return JsonResponse(data=message, status=403)

    @auth_with_token
    @json_request(required_fields=('id',))
    def delete(self, request, data: dict, message: dict, *args, **kwargs):
        """ Удалить статью (перенести в архив).
        Обычному пользователю можно удалять только свои статьи.
        Админу можно удалять любые статьи.
        В теле запроса (`JSON`-формат)
        необходимо указать поле `id` - идентификатор статьи.
        Возвращает сообщение с результатом и описание ошибки (если есть).
        """

        user: User = request.user
        article_id: int = int(data['id'])

        article: Article or None = Article.objects.filter(
            id=article_id, is_active=True).first()
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return JsonResponse(data=message, status=404)

        if (article.author.id == user.id) or user.is_superuser:
            article.delete()
            return JsonResponse(data=message, status=204)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act
            return JsonResponse(data=message, status=403)

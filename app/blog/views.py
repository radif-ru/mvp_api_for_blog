import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from config.settings import RESPONSE_MESSAGES
from users.decorators import user_auth_with_token
from .mixins import ViewParseRequestBodyMixin
from .models import Article, Comment


class ArticleView(ViewParseRequestBodyMixin,
                  View):

    def get(self, request, *args, **kwargs):
        """ Получить статьи.
        Все активные или при передаче параметра `id` - статью с комментариями
        по переданному идентификатору.
        """

        article_id: int = int(request.GET.get('id'))
        if article_id:
            article: Article = Article.objects.filter(id=article_id).first()
            comments: list = list(Comment.objects.filter(
                article_id=article_id).values())
            data: dict = {'id': article.id,
                          'title': article.title,
                          'text': article.text,
                          'author': article.author.username,
                          'comments': comments}
            json_data: str = json.dumps(data, ensure_ascii=False)
            return HttpResponse(content=json_data, status=200)

        articles: [Article] = Article.objects.filter(is_active=True)
        json_articles: str = json.dumps(list(articles.values()),
                                        ensure_ascii=False)
        return HttpResponse(content=json_articles, status=200)

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
            return HttpResponse(content=json.dumps(message), status=400)
        if not text:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.no_required_fields
            return HttpResponse(content=json.dumps(message), status=400)

        article: Article = Article.objects.create(author_id=user.id,
                                                  title=title, text=text)
        message['article_id']: str = article.id
        return HttpResponse(content=json.dumps(message), status=201)

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
            return HttpResponse(content=json.dumps(message), status=400)

        article: [Article] = Article.objects.filter(id=article_id,
                                                    is_active=True)
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return HttpResponse(content=json.dumps(message), status=404)

        if (article.first().author.id == user.id) or user.is_superuser:
            article.update(**data)
            return HttpResponse(content=json.dumps(message), status=200)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act
            return HttpResponse(content=json.dumps(message), status=403)

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
            return HttpResponse(content=json.dumps(message), status=400)

        article: Article or None = Article.objects.filter(
            id=article_id, is_active=True).first()
        if not article:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.not_found
            return HttpResponse(content=json.dumps(message), status=404)

        if (article.author.id == user.id) or user.is_superuser:
            article.delete()
            return HttpResponse(content=json.dumps(message), status=204)
        else:
            message['status']: str = RESPONSE_MESSAGES.no_success
            message['error']: str = RESPONSE_MESSAGES.forbidden_act
            return HttpResponse(content=json.dumps(message), status=403)

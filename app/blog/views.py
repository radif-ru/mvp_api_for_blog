import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View

from blog.models import Article, Comment


def check_authorization(request):
    """ Проверить авторизацию """
    token: str = request.headers.get('Authorization')
    if not token:
        error: str = json.dumps({'error': 'no token'})
        return HttpResponse(content=error, status=401)
    user: User = User.objects.filter(token__token=token,
                                     token__is_active=True).first()
    if not user:
        error: str = json.dumps({'error': 'token is not valid'})
        return HttpResponse(content=error, status=401)

    return user


class ArticleView(View):
    def get(self, request, *args, **kwargs):
        """ Получить все статьи или статью с комментариями (по ID) """
        article_id: str = request.GET.get('id')
        if article_id:
            article_id: int = int(article_id)
            article = Article.objects.filter(id=article_id).first()
            comments: [] = list(Comment.objects.filter(
                article_id=article_id).values())
            data: dict = {'title': article.title,
                          'text': article.text,
                          'author': article.author.username,
                          'comments': comments}
            json_data: str = json.dumps(data, ensure_ascii=False)
            return HttpResponse(content=json_data, status=200)
        articles: [Article] = Article.objects.filter(is_active=True)
        json_articles: str = json.dumps(list(articles.values()),
                                        ensure_ascii=False)
        return HttpResponse(content=json_articles, status=200)

    def post(self, request, *args, **kwargs):
        """ Создать статью """

        check_result = check_authorization(request)
        if check_result is HttpResponse:
            return check_result
        user: User = check_result

        title: str = request.POST.get('title')
        text: str = request.POST.get('text')

        if not title:
            error: str = json.dumps({'error': 'no title'})
            return HttpResponse(content=error, status=400)
        if not text:
            error: str = json.dumps({'error': 'no text'})
            return HttpResponse(content=error, status=400)

        Article.objects.create(author_id=user.id, title=title, text=text)

        return HttpResponse(status=201)

    def patch(self, request, *args, **kwargs):
        """ Изменить статью """
        check_result = check_authorization(request)
        if check_result is HttpResponse:
            return check_result
        user: User = check_result

        body: [] = request.body.decode('utf-8').split('\r\n')
        data: dict = {}
        article_id = 0
        for num, el in enumerate(body, start=0):
            if 'name="title"' in el:
                data['title'] = body[num + 2]
            elif 'name="text"' in el:
                data['text'] = body[num + 2]
            elif 'name="id"' in el:
                article_id: int = body[num + 2]
        if 'title' not in data and 'text' not in data:
            error: str = json.dumps({'error': 'need to change title or text'})
            return HttpResponse(content=error, status=400)
        if article_id:
            article = Article.objects.filter(id=int(article_id),
                                             is_active=True)

            if (
                    article and article.first().author.id == user.id
            ) or user.is_superuser:
                result = article.update(**data)
                if not result:
                    return HttpResponse(status=204)
                return HttpResponse(status=200)

        error: str = json.dumps({'error': 'forbidden act'})
        return HttpResponse(content=error, status=400)

    def delete(self, request, *args, **kwargs):
        """ Удалить статью (перенести в архив) """
        check_result = check_authorization(request)
        if check_result is HttpResponse:
            return check_result
        user: User = check_result

        body: [] = request.body.decode('utf-8').split('\r\n')
        article_id = 0
        for num, el in enumerate(body, start=0):
            if 'name="id"' in el:
                article_id: int = body[num + 2]

        if article_id:
            article = Article.objects.filter(id=int(article_id),
                                             is_active=True)

            if (
                    article and article.first().author.id == user.id
            ) or user.is_superuser:
                article.update(is_active=False)
                return HttpResponse(status=200)

        error: str = json.dumps({'error': 'forbidden act'})
        return HttpResponse(content=error, status=400)

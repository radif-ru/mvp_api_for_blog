from django.contrib.auth.models import User
from django.db import models

from mixins.model import ModelDeleteMixin, ModelPieceTextMixin


class Article(ModelDeleteMixin, ModelPieceTextMixin, models.Model):
    """ Модель статьи """
    author = models.ForeignKey(User, verbose_name='автор',
                               on_delete=models.CASCADE, null=False,
                               blank=False)
    title = models.CharField(verbose_name='название', max_length=150,
                             null=False, blank=False)
    text = models.TextField(verbose_name='статья', null=False, blank=False)
    is_active = models.BooleanField(verbose_name='активность', default=True,
                                    null=False, blank=False)

    def __str__(self):
        return f'{self.title:.50}... ({self.id})'

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


class Comment(ModelPieceTextMixin, models.Model):
    """ Модель комментария к статье """
    article = models.ForeignKey(Article, verbose_name='статья',
                                on_delete=models.CASCADE, null=False,
                                blank=False)
    user = models.ForeignKey(User, verbose_name='автор комментария',
                             on_delete=models.CASCADE, null=False,
                             blank=False)
    text = models.CharField(verbose_name='комментарий', max_length=255,
                            null=False,
                            blank=False)

    def __str__(self):
        return f'{self.text:.50}... ({self.id})'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

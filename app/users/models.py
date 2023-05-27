from django.contrib.auth.models import User
from django.db import models

from mixins.model import ModelDeleteMixin


class Token(ModelDeleteMixin, models.Model):
    """ Модель токена """
    user = models.ForeignKey(User, verbose_name='пользователь',
                             on_delete=models.CASCADE, null=False, blank=False)
    token = models.CharField(verbose_name='токен', max_length=150, null=False,
                             blank=False)
    is_active = models.BooleanField(verbose_name='активность', default=True,
                                    null=False, blank=False)

    def __str__(self):
        return f'{self.token} ({self.id})'

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'
        # У пользователя может быть несколько токенов, но не 2 одинаковых
        unique_together = ('token', 'user')

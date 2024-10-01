from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.validators import username_validator


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=(username_validator,),
        error_messages={
            'unique': ('Пользователь с таким именем уже существует'),
        },
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LENGTH_FIRST_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LENGTH_LAST_NAME,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.get_username()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subsription',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_not_self'
            ),
        ]

    def __str__(self) -> str:
        return (f'Подписка {self.user.get_username()} '
                f'на {self.author.get_username()}')

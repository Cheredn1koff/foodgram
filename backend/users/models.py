from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
        null=False,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAX_LENGTH_USER,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_username, ]
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_LENGTH_USER,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_LENGTH_USER,
        blank=False,
        null=False
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.MAX_LENGTH_USER,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

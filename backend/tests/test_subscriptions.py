from http import HTTPStatus

import pytest
from django.urls import reverse

from users.models import Subscription
from tests.utils import check_fields_in_response


@pytest.mark.django_db(transaction=True)
class TestSubscriptionsAPI:
    subscriptions_url = reverse('users-subscriptions')

    def test_access_not_authenticated_subscription_list(
            self, client
    ):
        '''Проверка существования эндпоинта подписок и наличия
        доступа к нему у неавторизованного пользователя
        '''
        response = client.get(self.subscriptions_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.subscriptions_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.subscriptions_url}` возвращает код 401'
        )

    def test_subscription_list(
            self, user_client, subscription_1, user,
            another_user, recipe_2
    ):
        '''Проверка корректности работы эндпоинта users/subscriptions/ при
        GET-запросе авторизованного пользователя
        '''
        response = user_client.get(self.subscriptions_url)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.subscriptions_url}` возвращает код 200'
        )

        response_json = response.json()
        assert 'results' in response_json and isinstance(
            response_json['results'], list
        ), (
            'Проверьте, что ответ GET-запрос неавторизованного '
            f'пользователя к `{self.subscriptions_url}` возвращает '
            'список пользователей, на которых подписан пользователь'
        )

        subscriptions = response_json['results']
        assert len(subscriptions) == Subscription.objects.filter(
            user=user
        ).count(), (
            'Проверьте, что ответ GET-запрос неавторизованного '
            f'пользователя к `{self.subscriptions_url}` возвращает '
            'все его подписки'
        )

        subscribed_user = subscriptions[0]
        subscribed_user_fields = {
            'id': another_user.id,
            'username': another_user.username,
            'first_name': another_user.first_name,
            'last_name': another_user.last_name,
            'is_subscribed': True,
            'recipes_count': another_user.recipes.count()
        }

        check_fields_in_response(
            subscribed_user_fields, subscribed_user, self.subscriptions_url
        )

    def test_access_not_authenticated_subscription_create(
            self, client, user
    ):
        '''Проверка существования эндпоинта подписок и наличия
        доступа к нему у неавторизованного пользователя
        '''
        subscription_create_url = reverse(
            'users-subscribe',
            kwargs={'id': user.id}
        )
        response = client.post(subscription_create_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{subscription_create_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{subscription_create_url}` возвращает код 401'
        )

    def test_subscription_create(self, user_client, user, another_user):
        '''Проверка корректности добавления подписки'''
        subscription_create_url = reverse(
            'users-subscribe',
            kwargs={'id': another_user.id}
        )
        subscription_before = Subscription.objects.filter(
            user=user,
            author=another_user
        ).exists()
        response = user_client.post(subscription_create_url)
        subscription_after = Subscription.objects.filter(
            user=user,
            author=another_user
        ).exists()
        assert response.status_code == HTTPStatus.CREATED, (
            'Проверьте, что в ответ на POST-запрос авторизованного'
            f'пользователя к {subscription_create_url} возвращается код 201'
        )
        assert not subscription_before and subscription_after, (
            'Проверьте, что POST-запрос авторизованного '
            f'пользователя к {subscription_create_url} создаёт подписку'
        )

        fields = {
            'id': another_user.id,
            'username': another_user.username,
            'first_name': another_user.first_name,
            'last_name': another_user.last_name,
            'is_subscribed': True,
            'recipes_count': another_user.recipes.count()
        }
        check_fields_in_response(
            fields, response.json(), subscription_create_url
        )

    def test_subscription_create_unique(self, user_client, another_user, user):
        '''Проверка уникальности создаваемой подписки'''
        subscription_create_url = reverse(
            'users-subscribe',
            kwargs={'id': another_user.id}
        )
        user_client.post(subscription_create_url)
        invalid_response = user_client.post(subscription_create_url)
        subscription_count = Subscription.objects.filter(
            user=user,
            author=another_user
        ).count()
        assert invalid_response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что в ответ на повторный POST-запрос авторизованного'
            f'пользователя к {subscription_create_url} возвращается код 400'
        )
        assert subscription_count == 1, (
            'Проверьте, что при повторном POST-запросе авторизованного '
            f'пользователя к {subscription_create_url} не создаётся ещё '
            'одной записи в БД'
        )

    def test_self_subscription_create_not_allowed(
            self, user_client, user
    ):
        '''Проверка подписки пользователя на самого себя'''
        subscription_create_url = reverse(
            'users-subscribe',
            kwargs={'id': user.id}
        )
        user_client.post(subscription_create_url)
        invalid_response = user_client.post(subscription_create_url)
        subscription_count = Subscription.objects.count()
        assert invalid_response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что в ответ POST-запрос авторизованного'
            f'пользователя к {subscription_create_url}, содержащем свой id, '
            'возвращается код 400. Пользователь не может подписаться на себя.'
        )
        assert Subscription.objects.count() == subscription_count, (
            'Проверьте, что при POST-запросе авторизованного '
            f'пользователя к {subscription_create_url} по своему id '
            'не создаётся записи в БД. Пользователь не может '
            'подписаться на себя.'
        )

    def test_access_not_authenticated_subscription_delete(
            self, client, another_user, subscription_1
    ):
        '''Проверка наличия доступа к удалению подписки
        неавторизованным пользователем
        '''
        subscription_delete_url = reverse(
            'users-subscribe',
            kwargs={'id': another_user.id}
        )
        response = client.delete(subscription_delete_url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{subscription_delete_url}` возвращает код 401'
        )

    def test_subscription_delete_by_author(
            self, user_client, subscription_1, another_user, user,
    ):
        '''Проверка корректности удаления из избранного автором объекта'''
        subscription_delete_url = reverse(
            'users-subscribe',
            kwargs={'id': another_user.id}
        )
        response = user_client.delete(subscription_delete_url)

        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос автора подписки к '
            f'`{subscription_delete_url}` возвращает код 204'
        )
        deleted_subscription = Subscription.objects.filter(
            user=user,
            author=another_user
        ).first()

        assert not deleted_subscription, (
            'Проверьте, что DELETE-запрос автора к '
            f'`{subscription_delete_url}` удаляет подписку'
        )

from http import HTTPStatus

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse

from tests.utils import (
    check_fields_in_response,
    check_only_safe_methods_allowed
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUsersAPI:
    user_list_url = reverse('users-list')
    user_me_url = reverse('users-me')
    set_password_url = reverse('users-set-password')

    def test_acces_not_authenticated_users_list(self, client):
        '''
        Проверка существования эндпоинта users/ и доступа к нему
        неавторизованного пользователя
        '''
        response = client.get(self.user_list_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.user_list_url}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.user_list_url}` возвращает код 200'
        )

    def test_users_list(self, client, user, another_user):
        '''Проверка эндпоинта со списком пользователей'''

        json_response = client.get(self.user_list_url).json()
        assert 'results' in json_response and isinstance(
            json_response['results'], list
        ), (
            f'Убедитесь, что в ответ на GET-запрос к `{self.user_list_url}'
            'по ключу `results` находится список'
        )
        users = json_response['results']
        assert len(users) == User.objects.count(), (
            f'Убедитесь, что в ответ на GET-запрос к `{self.user_list_url} '
            'в списке пользователей перечислены все пользователи'
        )

        user_data = users[0]
        user_fields = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': False
        }
        check_fields_in_response(user_fields, user_data, self.user_list_url)

    def test_acces_not_authenticated_user_detail(self, client, user):
        '''
        Проверка существования эндпоинта users/{id}/ и отсутствия
        доступа к нему неавторизованного пользователя
        '''

        response = client.get(reverse('users-detail', kwargs={'id': user.id}))
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.user_detail_url}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.user_detail_url}` возвращает код 401'
        )

    def test_user_detail(self, user_client, user):
        '''
        Проверка работы эндпоинта users/{id}/
        '''
        user_detail_url = reverse('users-detail', kwargs={'id': user.id})
        response = user_client.get(user_detail_url)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{user_detail_url}` возвращает код 200'
        )
        response_json = response.json()
        user_fields = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': False
        }
        check_fields_in_response(
            user_fields,
            response_json,
            user_detail_url
        )

    def test_user_detail_only_safe_methods_allowed(self, user_client, user):
        ''''
        Проверка, что с помощью эндпоинта /users/ нет
        возможности изменить пользователя
        '''
        check_only_safe_methods_allowed(
            user_client, reverse('users-detail', kwargs={'id': user.id})
        )

    def test_acces_not_authenticated_user_me(self, client):
        '''
        Проверка существования эндпоинта users/me/ и отсутствия
        доступа к нему неавторизованного пользователя
        '''

        response = client.get(self.user_me_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.user_me_url}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.user_me_url}` возвращает код 401'
        )

    def test_user_me_only_safe_methods_allowed(self, user_client):
        '''
        Проверка, что с помощью эндпоинта /users/me/ нет
        возможности изменить пользователя
        '''
        check_only_safe_methods_allowed(user_client, reverse('users-me'))

    def test_user_me(self, user_client, user):
        '''
        Проверка работы эндпоинта users/me/
        '''
        response = user_client.get(self.user_me_url)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.user_me_url}` возвращает код 200'
        )
        response_json = response.json()
        user_fields = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': False
        }
        check_fields_in_response(user_fields, response_json, self.user_me_url)

    def test_acces_not_authenticated_set_password(self, client):
        response = client.post(self.set_password_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_users}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.url_users}` возвращает код 401'
        )

    def test_set_password_with_no_data(self, user_client, user, password):
        '''
        Проверка, что попытка сменить пароль с незаполненными полями не
        приводит к смене пароля
        '''
        response = user_client.post(self.set_password_url)

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.set_password_url}` с пустыми данными возвращает'
            'ответ со статусом 400'
        )

        response_json = response.json()

        empty_fields = ['new_password', 'current_password']
        for field in empty_fields:
            assert (
                field in response_json
                and isinstance(response_json.get(field), list)
            ), (
                f'Если в POST-запросе к `{self.set_password_url}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях. Не отображена '
                f'информация о поле {field}'
            )

    def test_set_password_with_invalid_data(self, user_client):
        '''
        Проверка корректности работы эндпоинта смены пароля
        с запросом, содержащим невалидные данные
        '''

        invalid_data = {
            'current_password': 'UncorrectPassword',
            'new_password': ' '
        }

        response = user_client.post(self.set_password_url, data=invalid_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, что POST-запрос к `{self.set_password_url}` с '
            'невалидными данными возвращает статус 400'
        )

        response_json = response.json()
        invalid_fields = [
            'current_password',
            'new_password',
        ]
        for field in invalid_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в  POST-запросе к `{self.set_password_url}` переданы '
                'некорректные данные, в ответе должна возвращаться информация '
                'о неправильно заполненных полях.'
            )

    def test_set_password_with_valid_data(self, user_client, user, password):
        '''
        Проверка корректности работы эндпоинта смены пароля
        с запросом, содержащим валидные данные
        '''
        valid_data = {
            'current_password': password,
            'new_password': 'SomeNewPassword'
        }

        response = user_client.post(self.set_password_url, data=valid_data)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что POST-запрос с корректными данными к'
            f'{self.set_password_url} возвращает статус 204'
        )

        assert authenticate(
            username=user.username, password=valid_data['new_password']
        ), (
            'Проверьте, что POST-запрос с корректными данными к'
            f'{self.set_password_url} изменяет пароль пользователя'
        )

from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class TestTokenAuthAPI:

    def test_auth_token_login(self, client, user, password):
        ''''Тест эндпоинта /api/auth/token/login'''
        response = client.post(
            '/api/auth/token/login',
            data={'email': user.email, 'password': password}
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница "/api/auth/token/login" не найдена, проверьте этот '
            'адрес в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что POST-запрос к "/api/auth/token/login" '
            'возвращает ответ с кодом 200.'
        )
        auth_data = response.json()
        assert 'auth_token' in auth_data, (
            'Проверьте, что ответ на POST-запрос с валидными данными к '
            '/api/auth/token/login` содержит токен.'
        )

        response_with_error = client.post(
            '/api/auth/token/login',
            data={'password': password}
        )

        assert response_with_error.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос к "/api/auth/token/login" '
            'с неполнымми данными возвращает ответ с кодом 400.'
        )

    def test_auth_token_logout(self, user_client, token):
        ''''Тест эндпоинта /api/auth/token/logout'''

        response = user_client.post(
            '/api/auth/token/logout',
        )

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница "/api/auth/token/logout" не найдена, проверьте этот '
            'адрес в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что POST-запрос к "/api/auth/token/logout" '
            'возвращает ответ с кодом 204.'
        )

        data = response.data

        assert not data, (
            'Проверьте, что что POST-запрос к "/api/auth/token/logout" '
            'приходит пустой ответ'
        )

        response_expired_token = user_client.post(
            '/api/auth/token/logout/',
            data={'auth_token': token}
        )

        assert response_expired_token.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что повторный запрос c удалённым токеном '
            'возвращает ответ с кодом 401.'
        )

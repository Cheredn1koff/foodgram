from http import HTTPStatus

import pytest
from django.urls import reverse

from tests.utils import (check_fields_in_response,
                         check_only_safe_methods_allowed)


@pytest.mark.django_db(transaction=True)
class TestIngredeintsAPI:

    ingredients_list_url = reverse('ingredients-list')

    def test_acces_not_authenticated_ingredients_list(self, client):
        '''
        Проверка существования эндпоинта ingredients/ и наличия доступа к нему
        неавторизованного пользователя
        '''
        response = client.get(self.ingredients_list_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.ingredients_list_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.ingredients_list_url}` возвращает код 200'
        )

    def test_ingredients_list(self, client, ingredient_1):
        '''
        Проверка корректности работы эндпоинта ingredients/
        '''
        response_json = client.get(self.ingredients_list_url).json()

        ingredient_fields = {
            'id': ingredient_1.id,
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit.name
        }
        check_fields_in_response(
            ingredient_fields,
            response_json[0],
            self.ingredients_list_url
        )

    def test_acces_not_authenticated_ingredients_detail(
            self, client, ingredient_1
    ):
        '''
        Проверка существования эндпоинта ingredients/{id} и наличия доступа к
        нему неавторизованного пользователя
        '''
        ingredient_detail_url = reverse(
            'ingredients-detail', kwargs={'pk': ingredient_1.id}
        )
        response = client.get(ingredient_detail_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{ingredient_detail_url}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{ingredient_detail_url}` возвращает код 200'
        )

    def test_ingredient_detail(self, client, ingredient_1):
        '''Проверка корректности работы эндпоинта ingredients/{id}/'''
        ingredient_fields = {
            'id': ingredient_1.id,
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit.name
        }
        response_json = client.get(
            reverse('ingredients-detail', kwargs={'pk': ingredient_1.id})
        ).json()
        check_fields_in_response(
            ingredient_fields,
            response_json,
            reverse('ingredients-detail', kwargs={'pk': ingredient_1.id})
        )

    def test_ingredient_detail_only_safe_methods_allowed(
        self,
        client,
        ingredient_1
    ):
        '''' Проверка, что с помощью эндпоинта /users/ingredients/ нет
        возможности добавить или изменить ингредиент'''
        check_only_safe_methods_allowed(
            client,
            reverse('ingredients-detail', kwargs={'pk': ingredient_1.id})
        )

    def test_ingredient_filtering_by_name(
        self,
        client,
        ingredient_1,
        ingredient_2
    ):
        '''' Проверка корректности работы фильтрации по названию ингредиента'''

        json_filter_response = client.get(
            self.ingredients_list_url + f'?name={ingredient_1.name[-1]}'
        ).json()
        json_simple_response = client.get(self.ingredients_list_url).json()

        assert json_filter_response != json_simple_response, (
            'Проверьте, что фильтрация по вхождению символов в название '
            f'ингредиента для эндпоинта {self.ingredients_list_url} '
            'работает корректно'
        )

        json_filter_response = client.get(
            self.ingredients_list_url + f'?name={ingredient_1.name[0]}'
        ).json()

        assert json_filter_response == json_simple_response, (
            'Проверьте, что фильтрация по вхождению символов в название '
            f'ингредиента для эндпоинта {self.ingredients_list_url} '
            'работает корректно'
        )

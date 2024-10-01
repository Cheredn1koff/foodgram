from http import HTTPStatus

import pytest
from django.urls import reverse

from recipes.models import Tag
from tests.utils import (
    check_fields_in_response,
    check_only_safe_methods_allowed
)


@pytest.mark.django_db(transaction=True)
class TestTagsAPI:

    tags_list_url = reverse('tags-list')

    def test_not_authenticated_tags_list(self, client):
        '''
        Проверка существования эндпоинта tags/ и наличия доступа к нему
        неавторизованного пользователя
        '''
        response = client.get(self.tags_list_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.tags_list_url}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.tags_list_url}` возвращает код 200'
        )

    def test_tags_list(self, client, tag_1, tag_2):
        '''
        Проверка корректности работы эндпоинта tags/
        '''
        response_json = client.get(self.tags_list_url).json()

        assert isinstance(
            response_json, list
        ), (
            f'Убедитесь, что в ответе на GET-запрос к `{self.tags_list_url}'
            'теги представлены списком'
        )

        assert len(response_json) == Tag.objects.count(), (
            f'Убедитесь, что в ответ на GET-запрос к `{self.tags_list_url}'
            'приходит список, содержащий все существующие теги'
        )

        tag_fields = {
            'id': tag_1.id,
            'name': tag_1.name,
            'color': tag_1.color,
            'slug': tag_1.slug
        }
        check_fields_in_response(
            tag_fields,
            response_json[0],
            self.tags_list_url
        )

    def test_acces_not_authenticated_tags_detail(self, client, tag_1):
        '''
        Проверка существования эндпоинта tags/{id} и наличия доступа к нему
        неавторизованного пользователя
        '''
        tag_detail_url = reverse('tags-detail', kwargs={'pk': tag_1.id})
        response = client.get(tag_detail_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{tag_detail_url}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{tag_detail_url}` возвращает код 200'
        )

    def test_tag_detail(self, client, tag_1):
        '''Проверка корректности работы эндпоинта tags/{id}/'''
        tag_fields = {
            'id': tag_1.id,
            'name': tag_1.name,
            'color': tag_1.color,
            'slug': tag_1.slug
        }
        response_json = client.get(
            reverse('tags-detail', kwargs={'pk': tag_1.id})
        ).json()
        check_fields_in_response(
            tag_fields,
            response_json,
            reverse('tags-detail', kwargs={'pk': tag_1.id})
        )

    def test_tag_detail_only_safe_methods_allowed(self, client, tag_1):
        '''' Проверка, что с помощью эндпоинта /users/tags/ нет возможности
        изменить или добавить тег'''
        check_only_safe_methods_allowed(
            client, reverse('tags-detail', kwargs={'pk': tag_1.id})
        )

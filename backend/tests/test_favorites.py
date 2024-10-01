from http import HTTPStatus

import pytest
from django.urls import reverse

from recipes.models import Favorite
from tests.utils import check_fields_in_response


@pytest.mark.django_db(transaction=True)
class TestFavoriteAPI:

    def test_access_not_authenticated_favorite_create(self, client, recipe_1):
        '''Проверка существования эндпоинта recipe/1/favorite/ и наличия
        доступа к созданию объекта у неавторизованного пользователя
        '''
        favorite_url = reverse(
            'favorites-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = client.post(favorite_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{favorite_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{favorite_url}` возвращает код 401'
        )

    def test_favorite_create(self, user_client, recipe_1, user):
        '''Проверка корректности добавления рецепта в список избранного'''
        favorite_url = reverse(
            'favorites-list', kwargs={'recipe_id': recipe_1.id}
        )
        favorite_before = Favorite.objects.filter(
            recipe=recipe_1,
            user=user
        ).exists()
        response = user_client.post(favorite_url)
        favorite_after = Favorite.objects.filter(
            recipe=recipe_1,
            user=user
        ).exists()
        assert response.status_code == HTTPStatus.CREATED, (
            'Проверьте, что в ответ на POST-запрос авторизованного'
            f'пользователя к {favorite_url} возвращается код 201'
        )
        assert not favorite_before and favorite_after, (
            'Проверьте, что POST-запрос авторизованного'
            f'пользователя к {favorite_url} добавляет рецепт'
            'в избранное'
        )

        fields = {
            'id': recipe_1.id,
            'name': recipe_1.name,
            'image': (
                f'http://testserver/media{recipe_1.image.name}'
            ),
            'cooking_time': recipe_1.cooking_time
        }
        check_fields_in_response(fields, response.json(), favorite_url)

    def test_favorite_create_unique(self, user_client, recipe_1, user):
        '''Проверка уникальности добавления рецепта в список избранного'''
        favorite_url = reverse(
            'favorites-list', kwargs={'recipe_id': recipe_1.id}
        )
        user_client.post(favorite_url)
        invalid_response = user_client.post(favorite_url)
        favorite_count = Favorite.objects.filter(
            recipe=recipe_1,
            user=user
        ).count()
        assert invalid_response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что в ответ на повторный POST-запрос авторизованного'
            f'пользователя к {favorite_url} возвращается код 400'
        )
        assert favorite_count == 1, (
            'Проверьте, что при повторном POST-запросе авторизованного '
            f'пользователя к {favorite_url} не создаётся ещё одной записи в БД'
        )

    def test_access_not_authenticated_favorite_delete(self, client, recipe_1):
        '''Проверка наличия доступа к удалению из избранного
        неавторизованным пользователем
        '''
        favorite_url = reverse(
            'favorites-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = client.delete(favorite_url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{favorite_url}` возвращает код 401'
        )

    def test_favorite_delete_by_author(
            self, user_client, favorite, recipe_1, user
    ):
        '''Проверка корректности удаления из избранного автором объекта'''
        favorite_url = reverse(
            'favorites-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = user_client.delete(favorite_url)

        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос автора подписки к '
            f'`{favorite_url}` возвращает код 204'
        )
        deleted_favorite = Favorite.objects.filter(
            recipe=recipe_1,
            user=user
        ).first()

        assert not deleted_favorite, (
            'Проверьте, что DELETE-запрос автора подписки к '
            f'`{favorite_url}` удаляет рецепт из избранного'
        )

from http import HTTPStatus

import pytest
from django.urls import reverse

from recipes.models import Purchase
from tests.utils import check_fields_in_response


@pytest.mark.django_db(transaction=True)
class TestPurchaseAPI:

    def test_access_not_authenticated_purchase_create(self, client, recipe_1):
        '''Проверка существования эндпоинта recipe/1/purchase/ и наличия
        доступа к созданию объекта у неавторизованного пользователя
        '''
        purchase_url = reverse(
            'purchases-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = client.post(purchase_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{purchase_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{purchase_url}` возвращает код 401'
        )

    def test_purchase_create(self, user_client, recipe_1, user):
        '''Проверка корректности добавления рецепта в список покупок'''
        purchase_url = reverse(
            'purchases-list', kwargs={'recipe_id': recipe_1.id}
        )
        purchase_before = Purchase.objects.filter(
            recipe=recipe_1,
            user=user
        ).exists()
        response = user_client.post(purchase_url)
        purchase_after = Purchase.objects.filter(
            recipe=recipe_1,
            user=user
        ).exists()
        assert response.status_code == HTTPStatus.CREATED, (
            'Проверьте, что в ответ на POST-запрос авторизованного'
            f'пользователя к {purchase_url} возвращается код 201'
        )
        assert not purchase_before and purchase_after, (
            'Проверьте, что POST-запрос авторизованного'
            f'пользователя к {purchase_url} добавляет рецепт'
            'в покупки'
        )

        fields = {
            'id': recipe_1.id,
            'name': recipe_1.name,
            'image': (
                f'http://testserver/media{recipe_1.image.name}'
            ),
            'cooking_time': recipe_1.cooking_time
        }
        check_fields_in_response(fields, response.json(), purchase_url)

    def test_purchase_create_unique(self, user_client, recipe_1, user):
        '''Проверка уникальности добавления рецепта в список покупок'''
        purchase_url = reverse(
            'purchases-list', kwargs={'recipe_id': recipe_1.id}
        )
        user_client.post(purchase_url)
        invalid_response = user_client.post(purchase_url)
        purchase_count = Purchase.objects.filter(
            recipe=recipe_1,
            user=user
        ).count()
        assert invalid_response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что в ответ на повторный POST-запрос авторизованного'
            f'пользователя к {purchase_url} возвращается код 400'
        )
        assert purchase_count == 1, (
            'Проверьте, что при повторном POST-запросе авторизованного '
            f'пользователя к {purchase_url} не создаётся ещё одной записи в БД'
        )

    def test_access_not_authenticated_purchase_delete(self, client, recipe_1):
        '''Проверка наличия доступа к удалению из избранного
        неавторизованным пользователем
        '''
        purchase_url = reverse(
            'purchases-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = client.delete(purchase_url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{purchase_url}` возвращает код 401'
        )

    def test_purchase_delete_by_author(
            self, user_client, purchase, recipe_1, user
    ):
        '''Проверка корректности удаления из избранного автором объекта'''
        purchase_url = reverse(
            'purchases-list', kwargs={'recipe_id': recipe_1.id}
        )
        response = user_client.delete(purchase_url)

        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос автора подписки к '
            f'`{purchase_url}` возвращает код 204'
        )
        deleted_purchase = Purchase.objects.filter(
            recipe=recipe_1,
            user=user
        ).first()

        assert not deleted_purchase, (
            'Проверьте, что DELETE-запрос автора подписки к '
            f'`{purchase_url}` удаляет рецепт из покупок'
        )

    def test_acces_download_not_authenticated(self, client):
        '''Проверка существования эндпоинта
        recipes/download_the_shopping_cart и наличия
        доступа к нему у неавторизованного пользователя
        '''
        download_url = reverse('recipes-download-shopping-cart')
        response = client.get(download_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{download_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{download_url}` возвращает код 401'
        )

    def test_download_shopping_cart(
            self, user_client, purchase, user, ingredientrecipe_1
    ):
        '''Проверка GET-запроса к recipes/download_shopping_cart'''
        download_url = reverse('recipes-download-shopping-cart')
        response = user_client.get(download_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{download_url}` возвращает код 200'
        )
        assert response.headers['Content-Type'] == 'application/pdf', (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{download_url}` скачивает PDF-file'
        )

    def test_download_empty_shopping_cart(
            self, user_client
    ):
        '''Проверка GET-запроса к recipes/download_shopping_cart
        при пустой корзине
        '''
        download_url = reverse('recipes-download-shopping-cart')
        response = user_client.get(download_url)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что GET-запрос авторизованного пользователя к'
            f'`{download_url}` при пустой корзине возвращает код 400'
        )

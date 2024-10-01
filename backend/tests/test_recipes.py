import json
from http import HTTPStatus

import pytest
from django.urls import reverse

from recipes.models import IngredientRecipe, Recipe, Tag
from tests.utils import check_fields_in_response


@pytest.mark.django_db(transaction=True)
class TestRecipesAPI:

    recipes_url = reverse('recipes-list')
    base_64_image = (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAA'
        'AACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImW'
        'NoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
    )

    def test_access_not_authenticated_recipes_list(self, client):
        '''
        Проверка существования эндпоинта recipes/ и наличия доступа к нему
        неавторизованного пользователя
        '''

        response = client.get(self.recipes_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.recipes_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.recipes_url}` возвращает код 200'
        )

    def test_recipe_list(
            self, client,
            recipe_1, recipe_2,
            tag_1, tag_2,
            ingredientrecipe_1,
            user,
            ingredient_1, mock_media
    ):
        '''Проверка корректности работы эндпоинта /recipes/ для GET-запросов'''

        json_response = client.get(
            self.recipes_url + f'?tags={tag_1.slug}&tags={tag_2.slug}'
        ).json()

        assert 'results' in json_response and isinstance(
            json_response['results'], list
        ), (
            f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}'
            'по ключу `results` находится список'
        )

        recipes = json_response['results']

        assert len(recipes) == Recipe.objects.count(), (
            f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}`'
            'в списке рецептов содержатся все рецепты'
        )

        recipe = recipes[1]

        fields_types = {
            'id': int,
            'author': dict,
            'is_in_shopping_cart': bool,
            'image': str,
            'text': str,
            'name': str,
            'cooking_time': int,
            'tags': list,
            'ingredients': list
        }

        for field, type in fields_types.items():
            assert field in recipe, (
                f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}`'
                f'для каждого рецепта определено поле {field}'
            )

            assert isinstance(recipe[field], type), (
                f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}`'
                f'для каждого рецепта поле {field} определяется типом {type}'
            )

        recipe_fields = {
            'id': recipe_1.id,
            'name': recipe_1.name,
            'text': recipe_1.text,
            'cooking_time': recipe_1.cooking_time,
            'image': (
                f'http://testserver/media{recipe_1.image.name}'
            )
        }
        check_fields_in_response(recipe_fields, recipe, self.recipes_url)

        author = recipe['author']
        author_fields = {
            'email': user.email,
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_subscribed': False

        }
        check_fields_in_response(author_fields, author, self.recipes_url)

        ingredients = recipe['ingredients']
        assert len(ingredients) == recipe_1.ingredients.count(), (
            f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}`'
            f'для каждого рецепта выведены все ингредиенты'
        )

        ingredient = ingredients[0]
        ingredient_fields = {
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit.name,
            'amount': ingredientrecipe_1.amount,
            'id': ingredient_1.id,
        }
        check_fields_in_response(
            ingredient_fields, ingredient, self.recipes_url
        )

        tags = recipe['tags']
        assert len(tags) == recipe_1.tags.count(), (
            f'Проверьте, что в ответ на GET-запрос к `{self.recipes_url}`'
            f'для каждого рецепта выведены все ингредиенты'
        )
        tag = tags[0]
        tag_fields = {
            'name': tag_1.name,
            'color': tag_1.color,
            'slug': tag_1.slug,
            'id': tag_1.id,
        }
        check_fields_in_response(tag_fields, tag, self.recipes_url)

    def test_acces_not_authenticated_recipes_detail(self, client, recipe_1):
        '''
        Проверка существования эндпоинта recipes/{pk} и наличия доступа к нему
        неавторизованного пользователя
        '''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        response = client.get(recipe_detail_url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{recipe_detail_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{recipe_detail_url}` возвращает код 200'
        )

    def test_recipe_detail(
            self, client, recipe_1, ingredientrecipe_1,
            ingredient_1, tag_1, user
    ):
        '''Проверка корректности работы эндпоинта /recipes/<id>/
        для GET-запросов'''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        json_response = client.get(recipe_detail_url).json()

        # assert json_response

        recipe = json_response

        fields_types = {
            'id': int,
            'author': dict,
            'is_in_shopping_cart': bool,
            'image': str,
            'text': str,
            'name': str,
            'cooking_time': int,
            'tags': list,
            'ingredients': list
        }

        for field, type in fields_types.items():
            assert field in recipe, (
                f'Проверьте, что в ответ на GET-запрос к `{recipe_detail_url}`'
                f'для каждого рецепта определено поле {field}'
            )

            assert isinstance(recipe[field], type), (
                f'Проверьте, что в ответ на GET-запрос к `{recipe_detail_url}`'
                f'для каждого рецепта поле {field} определяется типом {type}'
            )

        recipe_fields = {
            'id': recipe_1.id,
            'name': recipe_1.name,
            'text': recipe_1.text,
            'cooking_time': recipe_1.cooking_time,
            'image': (
                f'http://testserver/media{recipe_1.image.name}'
            )
        }
        check_fields_in_response(recipe_fields, recipe, recipe_detail_url)

        author = recipe['author']
        author_fields = {
            'email': user.email,
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_subscribed': False

        }
        check_fields_in_response(author_fields, author, recipe_detail_url)

        ingredients = recipe['ingredients']
        assert len(ingredients) == recipe_1.ingredients.count(), (
            f'Проверьте, что в ответ на GET-запрос к `{recipe_detail_url}`'
            f'для каждого рецепта выведены все ингредиенты'
        )

        ingredient = ingredients[0]
        ingredient_fields = {
            'name': ingredient_1.name,
            'measurement_unit': ingredient_1.measurement_unit.name,
            'amount': ingredientrecipe_1.amount,
            'id': ingredient_1.id,
        }
        check_fields_in_response(
            ingredient_fields, ingredient, recipe_detail_url
        )

        tags = recipe['tags']
        assert len(tags) == recipe_1.tags.count(), (
            f'Проверьте, что в ответ на GET-запрос к `{recipe_detail_url}`'
            f'для каждого рецепта выведены все ингредиенты'
        )
        tag = tags[0]
        tag_fields = {
            'name': tag_1.name,
            'color': tag_1.color,
            'slug': tag_1.slug,
            'id': tag_1.id,
        }
        check_fields_in_response(tag_fields, tag, recipe_detail_url)

    def test_acces_not_authenticated_recipe_create_url(self, client):
        '''Проверка наличия доступа к эндпоинту созданию рецепта
        неваторизованного пользователя'''
        response = client.post(self.recipes_url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.recipes_url}` возвращает код 401'
        )

    def test_recipe_create_with_no_data(self, user_client):
        response = user_client.post(self.recipes_url)

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'без данных возвращает код 400'
        )

        response_json = response.json()

        required_fields = [
            'ingredients',
            'tags',
            'name',
            'image',
            'cooking_time',
            'text',
        ]
        for field in required_fields:
            assert field in response_json, (
                'Проверьте, что в ответе на POST-запрос к '
                f'`{self.recipes_url}` без данных возвращается'
                f'список необходимых полей. Поле {field} должно '
                'быть в списке'
            )

    def test_recipe_create_with_invalid_data(
            self, ingredient_1,
            ingredient_2, tag_1, user_client, mock_media
    ):
        '''Проверка корректности обработки невалидных данных для
        POST-запроса к эндпоинту recipes/'''
        data_with_incorrect_tags = {
            'ingredients': [
                {
                    'id': ingredient_1.id,
                    'amount': 10
                }
            ],
            'tags': [
                12344323462346,
            ],
            'image': self.base_64_image,
            'name': 'string',
            'text': 'string',
            'cooking_time': 1
        }

        data_with_incorrect_ingredients = {
            'ingredients': [
                {
                    'id': 12341235235,
                    'amount': 10
                }
            ],
            'tags': [
                tag_1.id,
            ],
            'image': self.base_64_image,
            'name': 'string',
            'text': 'string',
            'cooking_time': 1
        }

        for data in [
            data_with_incorrect_ingredients,
            data_with_incorrect_tags
        ]:
            data = json.dumps(data)
            recipes_count = Recipe.objects.count()
            response = user_client.post(
                self.recipes_url,
                data=data,
                content_type='application/json'
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                'Проверьте, что при POST-запросе с данными, содержащими '
                'несуществующие id для тегов/ингредиентов возвращается '
                'статус 404'
            )
            assert Recipe.objects.count() == recipes_count, (
                'Проверьте, что POST-запрос с данными, содержащими '
                'несуществующие id для тегов/ингредиентов '
                'не создаёт рецепт'
            )

        data_with_incorrect_type = {
            'ingredients': [
                {
                    'id': ingredient_1.id,
                    'amount': 10
                }
            ],
            'tags': [
                tag_1.id,
            ],
            'image': self.base_64_image,
            'name': [],
            'text': 'string',
            'cooking_time': 1
        }
        recipes_count = Recipe.objects.count()
        response = user_client.post(
            self.recipes_url,
            data=json.dumps(data_with_incorrect_type),
            content_type='application/json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при POST-запросе с данными, содержащими '
            'некорректные данные возвращается статус 400'
        )

        assert Recipe.objects.count() == recipes_count, (
            'Проверьте, что POST-запрос с данными, содержащими '
            'некорректные данные не создаёт рецепт'
        )

    def test_recipe_create_with_valid_data(
            self, user_client, ingredient_1, ingredient_2,
            tag_1, tag_2, mock_media
    ):
        '''Проверка, что POST-запрос с валидными данными к эндпоинту recipes/
        создаёт рецепт'''
        valid_data = {
            'ingredients': [
                {
                    'id': ingredient_1.id,
                    'amount': 10
                },
                {
                    'id': ingredient_2.id,
                    'amount': 10
                }
            ],
            'tags': [
                tag_1.id, tag_2.id
            ],
            'image': self.base_64_image,
            'name': 'string',
            'text': 'string',
            'cooking_time': 1
        }
        recipes_count = Recipe.objects.count()
        response = user_client.post(
            self.recipes_url,
            json.dumps(valid_data),
            content_type='application/json'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'с валидными данными возвращает код 201'
        )

        assert Recipe.objects.count() == recipes_count + 1, (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'с валидными данными создаёт рецепт в базе данных'
        )

        new_recipe = Recipe.objects.last()
        assert new_recipe.name == valid_data['name'], (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'корректно сохраняет данные в БД'
        )
        assert new_recipe.text == valid_data['text'], (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'корректно сохраняет данные в БД'
        )
        assert new_recipe.cooking_time == valid_data['cooking_time'], (
            f'Проверьте, что POST-запрос к `{self.recipes_url}` '
            'корректно сохраняет данные в БД'
        )
        for ingredient in valid_data['ingredients']:
            assert IngredientRecipe.objects.filter(
                ingredient__id=ingredient.get('id'),
                recipe=new_recipe,
                amount=ingredient.get('amount')
            ).exists(), (
                f'Проверьте, что POST-запрос к `{self.recipes_url}` '
                'создаёт связь между указанными ингредиентами и рецептом'
            )
        new_recipe_tags = new_recipe.tags.all()
        for tag_id in valid_data['tags']:
            assert Tag.objects.get(id=tag_id) in new_recipe_tags, (
                f'Проверьте, что POST-запрос к `{self.recipes_url}` '
                'создаёт связь между указанными тегами и рецептом'
            )

    def test_acces_not_authenticated_recipes_delete(
            self, client, recipe_1, mock_media
    ):
        '''Проверяет, что у неавторизованного пользователя нет доступа
        к удалению рецепта'''
        delete_recipe_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        response = client.delete(delete_recipe_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.recipes_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.recipes_url}` возвращает код 401'
        )

    def test_delete_recipe_by_author(self, user_client, recipe_1, mock_media):
        '''Проверяет, что автор рецепта может его удалить'''
        delete_recipe_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        recipes_count = Recipe.objects.count()
        response = user_client.delete(delete_recipe_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что POST-запрос автора рецепта к '
            f'`{self.recipes_url}` возвращает код 204'
        )
        assert Recipe.objects.count() == recipes_count - 1, (
            'Проверьте, что POST-запрос автора рецепта к '
            f'`{self.recipes_url}` удаляет рецепт'
        )

    def test_delete_recipe_not_by_author(
            self, another_user_client, recipe_1, mock_media
    ):
        '''Проверяет, что авторизованный пользователь может
        удалять только свои рецепты'''
        delete_recipe_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        recipes_count = Recipe.objects.count()
        response = another_user_client.delete(delete_recipe_url)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что POST-запрос автора рецепта к '
            f'`{self.recipes_url}` возвращает код 403'
        )
        assert Recipe.objects.count() == recipes_count, (
            'Проверьте, что POST-запрос не автора рецепта к '
            f'`{self.recipes_url}` не удаляет рецепт'
        )

    def test_delete_recipe_by_admin(
            self, admin_user_client, recipe_1, mock_media
    ):
        '''Проверяет, что администратор может удалить любой рецепт'''
        delete_recipe_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        recipes_count = Recipe.objects.count()
        response = admin_user_client.delete(delete_recipe_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что POST-запрос админа к '
            f'`{self.recipes_url}` возвращает код 204'
        )
        assert Recipe.objects.count() == recipes_count - 1, (
            'Проверьте, что POST-запрос админа к '
            f'`{self.recipes_url}` удаляет рецепт'
        )

    def test_acces_not_authenticated_recipes_patch(
            self, client, recipe_1, mock_media
    ):
        '''Проверка, что неаутентифицированный пользователь не может
        изменить рецепт'''
        patch_recipe_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        response = client.patch(patch_recipe_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.recipes_url}` не найден.'
            'Проверьте настройки в *urls.py*.'
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что PATCH-запрос неавторизованного пользователя к '
            f'`{self.recipes_url}` возвращает код 401'
        )

    def test_patch_recipes_with_invalid_data(
            self, user_client, recipe_1, ingredient_1, mock_media
    ):
        '''Проверка, что PATCH-запрос с невалиднными данными
        не изменяет рецепт'''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )

        empty_ingredients = {
            'ingredients': []
        }
        invalid_ingredients = {
            'ingredients': [
                {
                    'id': ingredient_1.id,
                    'amount': -100
                }
            ]
        }
        empty_tags = {
            'tags': []
        }
        invalid_fields = {
            'cooking_time': 'srting'
        }

        invalid_datas = [
            empty_ingredients,
            invalid_ingredients,
            empty_tags,
            invalid_fields
        ]
        for data in invalid_datas:
            response = user_client.patch(
                recipe_detail_url,
                data=json.dumps(data),
                content_type='application/json'
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f'Проверьте, что PATCH-запрос к {recipe_detail_url}'
                'с невалидными данными возвращает код 400'
            )

    def test_author_patch_recipes_with_valid_data(
            self, user_client, recipe_1, ingredient_1, ingredient_2,
            tag_1, tag_2, mock_media
    ):
        '''Проверка, что PATCH-запрос автора с валидными данными
        изменяет рецепт'''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        valid_data = {
            'ingredients': [
                {
                    'id': ingredient_2.id,
                    'amount': 11
                }
            ],
            'tags': [
                tag_2.id,

            ],
            'image': self.base_64_image,
            'name': 'another_string',
            'text': 'another_string',
            'cooking_time': 2
        }

        response = user_client.patch(
            recipe_detail_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        recipe = Recipe.objects.get(id=recipe_1.id)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос автора рецепта к '
            f'`{recipe_detail_url}` возвращает код 200'
        )

        assert recipe.ingredients.filter(
            ingredient__id=ingredient_2.id
        ).exists(), (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert not recipe.ingredients.filter(
            ingredient__id=ingredient_1.id
        ).exists(), (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )

        assert recipe.name == valid_data['name'], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert recipe.cooking_time == valid_data[
            'cooking_time'
        ], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert recipe.text == valid_data['text'], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )

    def test_admin_patch_recipes_with_valid_data(
        self, admin_user_client, recipe_1, ingredient_1, ingredient_2,
        tag_1, tag_2, mock_media
    ):
        '''Проверка, что PATCH-запрос админа с валидными данными
        изменяет рецепт'''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )
        valid_data = {
            'ingredients': [
                {
                    'id': ingredient_2.id,
                    'amount': 11
                }
            ],
            'tags': [
                tag_2.id,

            ],
            'image': self.base_64_image,
            'name': 'another_string',
            'text': 'another_string',
            'cooking_time': 2
        }

        response = admin_user_client.patch(
            recipe_detail_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        recipe = Recipe.objects.get(id=recipe_1.id)

        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос автора рецепта к '
            f'`{self.recipes_url}` возвращает код 200'
        )

        assert recipe.ingredients.filter(
            ingredient__id=ingredient_2.id
        ).exists(), (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert not recipe.ingredients.filter(
            ingredient__id=ingredient_1.id
        ).exists(), (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )

        assert recipe.name == valid_data['name'], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert recipe.cooking_time == valid_data[
            'cooking_time'
        ], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )
        assert recipe.text == valid_data['text'], (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'корректно изменяет данные в БД'
        )

    def test_another_user_patch_recipe(
            self, another_user_client, tag_2,
            ingredient_2, recipe_1, mock_media
    ):
        '''Проверка, что не автор рецепта не может его изменить'''
        recipe_detail_url = reverse(
            'recipes-detail', kwargs={'pk': recipe_1.id}
        )

        valid_data = {
            'ingredients': [
                {
                    'id': ingredient_2.id,
                    'amount': 11
                }
            ],
            'tags': [
                tag_2.id,

            ],
            'image': self.base_64_image,
            'name': 'another_string',
            'text': 'another_string',
            'cooking_time': 2
        }

        response = another_user_client.patch(
            recipe_detail_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте, что PATCH-запрос к `{recipe_detail_url}` '
            'от пользователя, не являющегося автором рецепта'
            'не изменяет его'
        )

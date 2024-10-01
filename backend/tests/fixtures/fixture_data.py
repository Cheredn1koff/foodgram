import tempfile

import pytest

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag, Unit
)
from users.models import Subscription


@pytest.fixture()
def mock_media(settings):
    with tempfile.TemporaryDirectory() as temp_directory:
        settings.MEDIA_ROOT = temp_directory
        yield temp_directory


@pytest.fixture
def tag_1():
    return Tag.objects.create(
        name='TestTag1',
        slug='TestTagSlug1',
        color='#b03f95'
    )


@pytest.fixture
def tag_2():
    return Tag.objects.create(
        name='TestTag2',
        slug='TestTagSlug2',
        color='#b03f96'
    )


@pytest.fixture
def unit():
    return Unit.objects.create(
        name='UnitName'
    )


@pytest.fixture
def ingredient_1(unit):
    return Ingredient.objects.create(
        name='IngredientName1',
        measurement_unit=unit,
    )


@pytest.fixture
def ingredient_2(unit):
    return Ingredient.objects.create(
        name='IngredientName2',
        measurement_unit=unit,
    )


@pytest.fixture
def recipe_1(user, tag_1):
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    recipe = Recipe.objects.create(
        name='TestRecipe',
        text='TextTestRecipe',
        cooking_time=150,
        author=user,
        image=image
    )
    recipe.tags.set([tag_1])
    return recipe


@pytest.fixture
def recipe_2(user, tag_1, tag_2):
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    recipe = Recipe.objects.create(
        name='TestRecipe2',
        text='TextTestRecipe2',
        cooking_time=150,
        author=user,
        image=image
    )
    recipe.tags.set([tag_1, tag_2])
    return recipe


@pytest.fixture
def ingredientrecipe_1(recipe_1, ingredient_1):
    return IngredientRecipe.objects.create(
        recipe=recipe_1,
        ingredient=ingredient_1,
        amount=10
    )


@pytest.fixture
def favorite(recipe_1, user):
    return Favorite.objects.create(
        recipe=recipe_1,
        user=user
    )


@pytest.fixture
def purchase(recipe_1, user):
    return Purchase.objects.create(
        recipe=recipe_1,
        user=user
    )


@pytest.fixture
def subscription_1(user, another_user):
    return Subscription.objects.create(
        user=user,
        author=another_user
    )

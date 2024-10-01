from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, IngredientRecipe, Tag


def collect_ingredientsrecipe_objects(ingredient_data, recipe):
    buffer = []
    for data in ingredient_data:
        ingredient = get_object_or_404(
            Ingredient,
            id=data['ingredient']['id']
        )
        buffer.append(IngredientRecipe(
            recipe=recipe,
            ingredient=ingredient,
            amount=data.get('amount')
        ))
    return buffer


def collect_tags(tag_data):
    buffer = []
    for tag_id in tag_data:
        tag = get_object_or_404(Tag, id=tag_id)
        buffer.append(tag)
    return buffer

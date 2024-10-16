import json

from django.core.management import BaseCommand
from recipes.models import Ingredient

ingredients = []


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в БД'

    def handle(self, *args, **options):
        with open(
                './data/ingredients.json',
                encoding='utf-8'
        ) as data:
            for row in json.load(data):
                ingredients.append(Ingredient(
                    name=row['name'].capitalize(),
                    measurement_unit=row['measurement_unit']
                ))
            Ingredient.objects.bulk_create(ingredients)

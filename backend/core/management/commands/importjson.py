import json

from django.conf import settings
from django.core.management.base import BaseCommand

from core.utils import load_ingredients_data


class Command(BaseCommand):
    help = settings.HELP_IMPORT_JSON_MESSAGE

    def handle(self, *args, **kwargs):
        with open(settings.JSON_PATH, 'rb') as json_file:
            data = json.load(json_file)
            load_ingredients_data(data)

        self.stdout.write(
            self.style.SUCCESS(
                settings.SUCCES_IMPORT_MESSAGE
            )
        )

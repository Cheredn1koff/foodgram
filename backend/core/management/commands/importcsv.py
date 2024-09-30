import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from core.utils import load_ingredients_data


class Command(BaseCommand):
    help = settings.HELP_IMPORT_CSV_MESSAGE

    def handle(self, *args, **kwargs):
        with open(settings.CSV_PATH, 'r') as csv_file:
            data = csv.DictReader(csv_file)
            load_ingredients_data(data)

        self.stdout.write(
            self.style.SUCCESS(
                settings.SUCCES_IMPORT_MESSAGE
            )
        )

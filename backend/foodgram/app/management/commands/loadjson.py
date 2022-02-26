import json

from django.core.management.base import BaseCommand

from app.models import Ingredients


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="file path")

    def handle(self, *args, **options):
        file_path = options["path"]

        with open(file_path, encoding='utf-8') as f:

            data = json.load(f)
            for item in data:
                Ingredients.objects.create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'])

import csv
import os

from django.apps import apps
from django.core.management import BaseCommand

app_models = apps.get_app_config('reviews').get_models()
filepaths = [
    file for file in os.listdir("static/data/") if file.endswith('.csv')
]


def iter_csv(file_path: str):
    try:
        with open(file_path, 'r') as inp_f:
            reader = csv.DictReader(inp_f)
            for row in reader:
                yield row
    except Exception as e:
        return f"Ошибка чтения csv-файла: {e}"


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            for file in filepaths:
                for model in app_models:
                    reader = iter_csv(file)
                    for row in reader:
                        model.objects.bulk_create(**row)
            return "Импорт БД завершён."
        except Exception as e:
            return f"Ошибка импорта: {e}"

import json
from django.core.management.base import BaseCommand
from analytics.models import Country

class Command(BaseCommand):
    help = 'Import countries from JSON file'

    def handle(self, *args, **kwargs):
        try:
            with open('analytics/fixtures/countries.json', 'r', encoding='utf-8') as f:
                countries = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ countries.json file not found!"))
            return

        created = 0
        for item in countries:
            obj, is_created = Country.objects.get_or_create(
                name=item['name'],
                code=item['code']
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {created} countries imported successfully!"))

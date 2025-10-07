import json
from django.core.management.base import BaseCommand
from chatbot.models import QA  # replace your_app with your app name

class Command(BaseCommand):
    help = 'Import QA from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                QA.objects.create(question=item['question'], answer=item['answer'])
        self.stdout.write(self.style.SUCCESS('QA data imported successfully!'))

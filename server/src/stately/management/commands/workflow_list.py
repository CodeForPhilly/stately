from django.core.management.base import BaseCommand, CommandError
from stately.models import Workflow

class Command (BaseCommand):
    help = 'Lists the workflows available in the database'

    def handle(self, *args, **options):
        for workflow in Workflow.objects.all():
            self.stdout.write(workflow.slug)

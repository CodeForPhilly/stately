from django.core.management.base import BaseCommand, CommandError
from stately.models import Workflow

class Command (BaseCommand):
    help = 'Imports one or more workflow configuration files'

    def add_arguments(self, parser):
        parser.add_argument('configfile', nargs='+', type=str)

    def handle(self, *args, **options):
        for config_filename in options['configfile']:
            self.stdout.write('Loading workflow from {}'.format(config_filename))
            Workflow.load_from_config_file(config_filename)

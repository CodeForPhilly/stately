from django.core.management.base import BaseCommand, CommandError
from stately.models import Workflow

class Command (BaseCommand):
    help = 'Deletes one or more workflow configurations from the database'

    def add_arguments(self, parser):
        parser.add_argument('slug', nargs='+', type=str)
        parser.add_argument('--noinput', '-y', dest='ask_confirmation', action='store_false', default=True)

    def handle(self, *args, **options):
        slugs = options['slug']

        if options['ask_confirmation']:
            confirmed = input('Really delete workflow(s) "{}" [y/N]: '.format('", "'.join(slugs)))
            confirmed = (confirmed == 'y')
        else:
            confirmed = True

        if confirmed:
            Workflow.objects.filter(slug__in=slugs).delete()
        else:
            self.stdout.write('Aborting.')

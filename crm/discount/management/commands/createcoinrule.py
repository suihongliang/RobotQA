from django.core.management.base import BaseCommand
from crm.discount.models import CoinRule


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('company_id', help='company_id', type=int)

    def handle(self, *args, **options):
        company_id = options['company_id']
        for category, value in CoinRule._meta.get_field('category').choices:
            try:
                CoinRule.objects.create(
                    category=category, company_id=company_id)
                self.stdout.write('{} created.'.format(value))
            except Exception:
                self.stdout.write('{} maybe exists.'.format(value))

from django.core.management.base import BaseCommand
from crm.discount.models import CoinRule


class Command(BaseCommand):
    help = 'Create Company default coin rule'

    def add_arguments(self, parser):
        parser.add_argument('company_id', help='company_id', type=int)

    def handle(self, *args, **options):
        company_id = options['company_id']
        for category, value in CoinRule._meta.get_field('category').choices:
            try:
                rule, created = CoinRule.objects.get_or_create(
                    category=category, company_id=company_id)
                if created:
                    self.stdout.write('{} created.'.format(value))
                else:
                    self.stdout.write('{} exists.'.format(value))
            except Exception:
                self.stdout.write('{} maybe exists.'.format(value))

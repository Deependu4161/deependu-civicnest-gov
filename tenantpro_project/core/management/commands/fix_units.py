"""
Run:  python manage.py fix_units
Creates missing Unit rows for any Property that has total_units > 0
but fewer actual Unit objects than declared.
"""
from django.core.management.base import BaseCommand
from core.models import Property, Unit


class Command(BaseCommand):
    help = 'Create missing Unit objects for existing properties'

    def handle(self, *args, **options):
        fixed = 0
        for prop in Property.objects.all():
            existing = prop.units.count()
            needed = prop.total_units - existing
            if needed <= 0:
                continue
            for i in range(existing + 1, prop.total_units + 1):
                Unit.objects.create(
                    property=prop,
                    unit_number=str(i),
                    floor=str((i - 1) // 4 + 1),
                    bedrooms=2,
                    monthly_rent=10000,
                    security_deposit=20000,
                    is_occupied=False,
                )
                fixed += 1
            self.stdout.write(
                self.style.SUCCESS(f'  {prop.name}: created {needed} unit(s)')
            )
        self.stdout.write(self.style.SUCCESS(f'\nDone — {fixed} units created total.'))

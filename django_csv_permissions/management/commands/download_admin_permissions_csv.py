from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Export Django admin model permissions per Group into a CSV file. (Scaffold)"

    def add_arguments(self, parser):
        parser.add_argument("--output", "-o", help="Path to output CSV file (optional). If omitted, prints to stdout.")

    def handle(self, *args, **options):
        raise CommandError("download_admin_permissions_csv is not yet implemented.")

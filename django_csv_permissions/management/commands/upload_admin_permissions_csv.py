from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import Django admin model permissions per Group from a CSV file. (Scaffold)"

    def add_arguments(self, parser):
        parser.add_argument("input", help="Path to input CSV file")
        parser.add_argument("--dry-run", action="store_true", help="Validate only; do not modify permissions")

    def handle(self, *args, **options):
        raise CommandError("upload_admin_permissions_csv is not yet implemented.")

import csv
import sys
from typing import List

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


def _permission_codename(action: str, model) -> str:
    opts = model._meta
    return f"{action}_{opts.model_name}"


class Command(BaseCommand):
    help = "Export Django admin model permissions per Group into a CSV file. Rows are models (app_label.ModelName). Columns are group permissions: for each Group, three columns [add, change, view]."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            help="Path to output CSV file (optional). If omitted, writes to stdout.",
        )
        parser.add_argument(
            "--all-models",
            action="store_true",
            help="Include all installed models (default).",
        )

    def handle(self, *args, **options):
        output = options.get("output")

        # Collect groups
        groups: List[Group] = list(Group.objects.all().order_by("name"))

        # Prepare header
        header = ["model"]
        for g in groups:
            header.extend([f"{g.name}__add", f"{g.name}__change", f"{g.name}__view"])

        # Collect models
        models = list(apps.get_models())

        rows: List[List[str]] = []
        for model in models:
            app_label = model._meta.app_label
            model_label = f"{app_label}.{model.__name__}"

            # Determine ContentType for permission lookup
            ct: ContentType = ContentType.objects.get_for_model(model)

            row = [model_label]
            for g in groups:
                for action in ("add", "change", "view"):
                    codename = _permission_codename(action, model)
                    has_perm = g.permissions.filter(codename=codename, content_type=ct).exists()
                    row.append("1" if has_perm else "")
            rows.append(row)

        # Write CSV
        if output:
            with open(output, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
                self.stdout.write(self.style.SUCCESS(f"Wrote permissions CSV to {output}"))
        else:
            writer = csv.writer(sys.stdout)
            writer.writerow(header)
            writer.writerows(rows)

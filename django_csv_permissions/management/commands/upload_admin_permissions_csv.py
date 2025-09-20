import csv
from typing import Dict, List, Tuple

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError


TRUTHY = {"1", "true", "t", "yes", "y", "on", "x"}
FALSY = {"0", "false", "f", "no", "n", "off", "none", "null"}


def parse_bool(value) -> bool:
    s = str(value).strip().lower()
    if s == "":
        return False
    if s in FALSY:
        return False
    if s in TRUTHY:
        return True
    # Any other non-empty value is considered truthy by spec
    return True


def _permission_codename(action: str, model) -> str:
    opts = model._meta
    return f"{action}_{opts.model_name}"


class Command(BaseCommand):
    help = "Import Django admin model permissions per Group from a CSV file. Any truthy value grants permission; falsy or empty revokes."

    def add_arguments(self, parser):
        parser.add_argument("input", help="Path to input CSV file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate only; do not modify permissions",
        )

    def handle(self, *args, **options):
        path = options["input"]
        dry_run = options["dry_run"]

        with open(path, newline="") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                raise CommandError("CSV file is empty")

            if not header or header[0].strip().lower() != "model":
                raise CommandError("First header column must be 'model'")

            # Parse group/action columns
            col_map: Dict[int, Tuple[Group, str]] = {}
            errors: List[str] = []
            seen_pairs = set()

            for idx, col in enumerate(header[1:], start=1):
                if "__" not in col:
                    errors.append(f"Invalid column '{col}'. Expected '<GroupName>__<action>'")
                    continue
                group_name, action = col.rsplit("__", 1)
                action = action.strip().lower()
                if action not in {"add", "change", "view"}:
                    errors.append(f"Invalid action '{action}' in column '{col}'. Must be add/change/view")
                    continue
                try:
                    group = Group.objects.get(name=group_name)
                except Group.DoesNotExist:
                    errors.append(f"Unknown group '{group_name}' referenced in header column '{col}'")
                    continue
                key = (group.pk, action)
                if key in seen_pairs:
                    errors.append(f"Duplicate column for group '{group_name}' action '{action}'")
                    continue
                seen_pairs.add(key)
                col_map[idx] = (group, action)

            if errors:
                raise CommandError("Invalid header: \n - " + "\n - ".join(errors))

            # Process rows
            changes_applied = 0
            changes_needed = 0
            row_num = 1  # counting header as row 1
            for row in reader:
                row_num += 1
                if not row:
                    continue
                model_label = (row[0] or "").strip()
                if not model_label or "." not in model_label:
                    raise CommandError(f"Row {row_num}: invalid model label '{model_label}'. Expected app_label.ModelName")
                app_label, model_name = model_label.split(".", 1)
                model = apps.get_model(app_label, model_name)
                if model is None:
                    raise CommandError(f"Row {row_num}: unknown model '{model_label}'")
                ct: ContentType = ContentType.objects.get_for_model(model)

                for idx, (group, action) in col_map.items():
                    value = row[idx] if idx < len(row) else ""
                    desired = parse_bool(value)
                    codename = _permission_codename(action, model)
                    perm = Permission.objects.filter(codename=codename, content_type=ct).first()
                    if not perm:
                        raise CommandError(
                            f"Row {row_num}: permission '{codename}' for model '{model_label}' does not exist"
                        )
                    has_now = group.permissions.filter(pk=perm.pk).exists()
                    if desired and not has_now:
                        changes_needed += 1
                        if not dry_run:
                            group.permissions.add(perm)
                            changes_applied += 1
                    elif not desired and has_now:
                        changes_needed += 1
                        if not dry_run:
                            group.permissions.remove(perm)
                            changes_applied += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run complete. Changes needed: {changes_needed}. No changes applied."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Import complete. Changes applied: {changes_applied}"))

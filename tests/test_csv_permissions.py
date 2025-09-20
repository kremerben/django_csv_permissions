import csv
import os
import tempfile

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase

from tests.sampleapp.models import Book


class CsvPermissionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editors = Group.objects.create(name="Editors")
        cls.viewers = Group.objects.create(name="Viewers")

        # Ensure permissions for Book exist
        ct = ContentType.objects.get_for_model(Book)
        model_name = Book._meta.model_name
        for action in ("add", "change", "view"):
            Permission.objects.get_or_create(
                codename=f"{action}_{model_name}",
                content_type=ct,
                defaults={"name": f"Can {action} Book"},
            )

        # Grant viewers the view permission by default
        view_perm = Permission.objects.get(codename=f"view_{model_name}", content_type=ct)
        cls.viewers.permissions.add(view_perm)

    def test_export_csv_contains_expected_columns_and_row(self):
        # Export to a temp file
        with tempfile.NamedTemporaryFile("w+", newline="", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            call_command("download_admin_permissions_csv", output=tmp_path, verbosity=0)
            with open(tmp_path, newline="") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                assert headers is not None
                self.assertIn("model", headers)
                self.assertIn("Editors__add", headers)
                self.assertIn("Editors__change", headers)
                self.assertIn("Editors__view", headers)
                self.assertIn("Viewers__view", headers)

                # Look for our model row
                found = False
                for row in reader:
                    if row["model"] == "sampleapp.Book":
                        found = True
                        self.assertEqual(row["Viewers__view"], "1")
                        self.assertEqual(row["Editors__view"], "")
                self.assertTrue(found, "Row for sampleapp.Book not found in export")
        finally:
            os.unlink(tmp_path)

    def test_import_csv_updates_permissions(self):
        # Build a CSV to grant Editors add + view, revoke Viewers view
        with tempfile.NamedTemporaryFile("w+", newline="", delete=False) as tmp:
            writer = csv.writer(tmp)
            writer.writerow(["model", "Editors__add", "Editors__change", "Editors__view", "Viewers__view"])
            writer.writerow(["sampleapp.Book", "1", "", "yes", "0"])
            tmp_path = tmp.name

        try:
            call_command("upload_admin_permissions_csv", tmp_path, verbosity=0)
            ct = ContentType.objects.get_for_model(Book)
            model_name = Book._meta.model_name
            add_perm = Permission.objects.get(codename=f"add_{model_name}", content_type=ct)
            view_perm = Permission.objects.get(codename=f"view_{model_name}", content_type=ct)

            self.assertTrue(self.editors.permissions.filter(pk=add_perm.pk).exists())
            self.assertTrue(self.editors.permissions.filter(pk=view_perm.pk).exists())
            self.assertFalse(self.viewers.permissions.filter(pk=view_perm.pk).exists())
        finally:
            os.unlink(tmp_path)

# Django CSV Permissions

A lightweight Django app that lets you export and import Django admin model permissions for Groups using a simple CSV file.

- Rows = models (formatted as `app_label.ModelName`).
- Columns = for each Group, three permission columns: `add`, `change`, `view`.
- Truthy values (e.g., `1`, `true`, `yes`, any non-empty string) mean “grant permission”. Falsy or empty values (e.g., `0`, `false`, `no`, or empty) mean “revoke permission”.

## Requirements
- Django 2.2+ (tested conceptually; includes `view` permission).

## Installation
1. Add the app to INSTALLED_APPS:
   - If installed as a local app, ensure the package directory `django_csv_permissions` is on your PYTHONPATH and add `"django_csv_permissions"` to `INSTALLED_APPS`.

2. Ensure `django.contrib.auth` and `django.contrib.contenttypes` are also in `INSTALLED_APPS` (standard in most Django projects).

## Commands

### Export admin permissions to CSV
Export a matrix of models by groups and their `add/change/view` permissions.

- To stdout:
  - `python manage.py download_admin_permissions_csv`

- To a file:
  - `python manage.py download_admin_permissions_csv --output permissions.csv`

The CSV includes a `model` column followed by three columns per Group (e.g., `Editors__add`, `Editors__change`, `Editors__view`).

### Import admin permissions from CSV
Read a CSV in the same format and update Group permissions accordingly.

- Apply updates:
  - `python manage.py upload_admin_permissions_csv permissions.csv`

- Dry run (validate and show intended changes without applying):
  - `python manage.py upload_admin_permissions_csv permissions.csv --dry-run`

Validation performed:
- First header cell must be `model`.
- Group/action columns must look like `<GroupName>__<action>` where `<action>` is one of `add`, `change`, `view`.
- Group names must exist in the database.
- Model labels must exist (e.g., `app_label.ModelName`).
- Permissions for the model must exist; otherwise the command errors.

Truthy/falsy rules:
- Truthy: `1`, `true`, `t`, `yes`, `y`, `on`, `x`, or any other non-empty string.
- Falsy: `0`, `false`, `f`, `no`, `n`, `off`, `none`, `null`, or empty.

## Development / Testing
This repository includes minimal tests and a sample app to validate behavior.

- A `manage.py` is included for convenience with `DJANGO_SETTINGS_MODULE=tests.settings`.
- Run tests (in an environment with Django installed):
  - `python manage.py test`  (or `python3 manage.py test`)

### What the tests cover
- Export: verifies the CSV contains expected headers and that the row for `sampleapp.Book` reflects permissions assigned to Groups.
- Import: verifies that changing CSV cells updates Group permissions accordingly.

## Notes
- Only `add`, `change`, and `view` permissions are handled per the requirement.
- If Groups are renamed between export and import, the header column names will no longer match. Keep group names stable across the process.
- The app exports permissions for all installed models. You can filter the CSV after export if needed.

## License
MIT (or according to your project’s licensing).
import os
import re
import datetime
import importlib.util


def load_migration(path):
    spec = importlib.util.spec_from_file_location("migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Migration()


def run_migrations():
    today = datetime.datetime.now().date()
    migrations_dir = "migrations"
    migration_files = [f for f in os.listdir(migrations_dir) if re.match(r'\d{4}_\d{2}_\d{2}_\d{3}_.*\.py$', f)]
    migration_files.sort()

    for filename in migration_files:
        date_part = filename.split("_", 3)[:3]
        migration_date = datetime.date(int(date_part[0]), int(date_part[1]), int(date_part[2]))

        if migration_date <= today:
            path = os.path.join(migrations_dir, filename)
            migration = load_migration(path)
            print(f"Running migration: {filename}")
            migration.run()


if __name__ == "__main__":
    run_migrations()

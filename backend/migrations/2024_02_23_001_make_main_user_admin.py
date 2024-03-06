import logging
import os

from models.admin import Admin
from models.role import Role
from mongoengine import connect
from passlib.handlers.bcrypt import bcrypt

MONGODB_URL = os.getenv("MONGODB_URL")
MAIN_USER_EMAIL = os.getenv("MAIN_USER_EMAIL")
MAIN_USER_PASSWORD = os.getenv("MAIN_USER_PASSWORD")
MAIN_USER_NAME = os.getenv("MAIN_USER_NAME")

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:  %(asctime)s  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class Migration:
    def run(self):
        connect(host=MONGODB_URL)

        admin_role = Role.objects(name='Admin').first()

        if not Admin.objects(email=MAIN_USER_EMAIL, is_active=True).first():
            admin: Admin = Admin(name=MAIN_USER_NAME, email=MAIN_USER_EMAIL, password=bcrypt.hash(MAIN_USER_PASSWORD),
                                 role=admin_role).save()
            logging.info(f"Main admin with id = {admin.id} created.")


if __name__ == "__main__":
    migration = Migration()
    migration.run()

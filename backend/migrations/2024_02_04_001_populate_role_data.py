import logging
import os

from mongoengine import connect

from models.role import Role
from models.user import User
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

        roles = ['Customer', 'Admin', 'Not_assigned']
        for role_name in roles:
            if not Role.objects(name=role_name).first():
                Role.objects.create(name=role_name)
                logging.info(f"Role '{role_name}' created.")

        admin_role = Role.objects(name='Admin').first()

        if not User.objects(email=MAIN_USER_EMAIL):
            User(name=MAIN_USER_NAME, email=MAIN_USER_EMAIL, password=bcrypt.hash(MAIN_USER_PASSWORD),
                 role=admin_role).save()
            logging.info("Main user created.")


if __name__ == "__main__":
    migration = Migration()
    migration.run()

from django.core.management import BaseCommand
from django.db import connections
import time
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting for database....")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waiting for a second....")
                time.sleep(1)

            self.stdout.write(self.style.SUCCESS("DATABASE AVAILABLE"))

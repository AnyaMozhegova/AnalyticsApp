import logging
import os

from mongoengine import connect

from models.report_indicator import ReportIndicator

MONGODB_URL = os.getenv("MONGODB_URL")

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:  %(asctime)s  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class Migration:
    def run(self):
        connect(host=MONGODB_URL)

        report_indicators = ['Median', 'Mean', 'Mode']
        for report_indicator in report_indicators:
            if not ReportIndicator.objects(name=report_indicator).first():
                ReportIndicator.objects.create(name=report_indicator)
                logging.info(f"Report Indicator '{report_indicator}' created.")


if __name__ == "__main__":
    migration = Migration()
    migration.run()

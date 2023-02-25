import logging
import os
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from scraper_procedures.config import *
from scraper_procedures.prescraping import prescrape
from scraper_procedures.scraping import scrape
from scraper_procedures.postprocessing import postprocess

""" Architectural Notes:
- [PRESCRAPE] Procedure
    - Operates on competition level
    - Scrape within the configured time range, grab all competition heads (competition name,
      and date info) from World Rowing API (scrapping_wr/api.py)
- [SCRAPE] Procedure
    - Operates on competition level
    - Scrape from World Rowing API (scrapping_wr/api.py) and write to db (model/dbutils.py)
    - Parse PDF Data & Merge/Assign Data to the right boat
- [POSTPROCESS] Procedure
    - Operates on the database as a whole
    - Go through the database that already has much data in it (robust basis for statistics)
    - Outlier Detection & Marking
    - World Best Times
    - Remove Inconsistencies
"""

def scheduler(duration=SCRAPER_SLEEP_TIME_SECONDS):
    logger = logging.getLogger("scheduler")

    logger.info(f"Waiting {duration} seconds ...")
    sleep(duration)

def start_service(singlepass=False):
    logger.info("[start_service]")
    while True:
        prescrape()
        scrape(parse_pdf=True)
        postprocess()

        if SCRAPER_SINGLEPASS or singlepass:
            logger.info("Override Scheduler")
            break

        scheduler()

if __name__ == '__main__':
    import argparse

    procedures = {
        "prescrape": prescrape,
        "scrape": scrape,
        "postprocess": postprocess
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--procedure", help="Procedure to run",
        choices=list(procedures.keys()), action="append"
    )
    parser.add_argument("-s", "--singlepass", help="Ignore the scheduler. Script exits after one pass.", action="store_true")
    args = parser.parse_args()
    logger.info(args)

    
    if not args.procedure:
        start_service(singlepass=args.singlepass)
    else:
        for procedure_id in args.procedure:
            function = procedures[procedure_id]
            function()

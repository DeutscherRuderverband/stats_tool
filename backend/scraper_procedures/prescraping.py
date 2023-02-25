import logging
import datetime

from sqlalchemy import select

from .config import *
from model import model
from model import dbutils
from scraping_wr import api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _scrape_range_half_year_window():
    today = datetime.date.today()
    second_half = today.month > 6
    if today.month > 6:
        return today.year, today.year+1
    return today.year-1, today.year

def _scrape_range_full_year_window():
    today = datetime.date.today()
    return today.year-1, today.year+1

def _scrape_range_max():
    today = datetime.date.today()
    year_max = today.year+1

    if SCRAPER_YEAR_MAX:
        year_max = SCRAPER_YEAR_MAX

    return SCRAPER_YEAR_MIN, year_max

def _detect_wr_scrapes(session):
    # HIGH-PRIO TODO: Introduce a field for source == WorldRowing
    statement = select(model.Competition.id).where(model.Competition.additional_id_ != None) 
    rows = session.execute(statement).first()
    detected = not rows == None
    return detected

def _scrape_competition_heads(session, year_min, year_max, logger=logger):
    if year_min > year_max:
        raise Exception(f"Year range is invalid: {year_min}-{year_max}")
    
    logger.info("Fetch all competition heads and write to db")
    for year in range(year_min, year_max+1):
        logger.info(f"Begin year={year} ---------------")
        competitions_wr = api.get_competition_heads([year], single_fetch=False)
        for competition_data in competitions_wr:
            logger.info(f'''Adding year={year} competition="{competition_data.get('id')}" name="{competition_data.get('DisplayName')}"''')
            dbutils.wr_insert(
                session,
                model.Competition,
                dbutils.wr_map_competition_prescrape,
                competition_data,
                overwrite_existing=False
            )


def prescrape(**kwargs):
    logger = logging.getLogger("prescrape")
    logger.info("Initialize Database")
    dbutils.create_tables(model.engine)

    year_min, year_max = _scrape_range_max()

    with model.Scoped_Session() as session:
        logger.info(f"Final decision for year range selection: {year_min}-{year_max}")
        _scrape_competition_heads(session=session, year_min=year_min, year_max=year_max, logger=logger)
        session.commit()
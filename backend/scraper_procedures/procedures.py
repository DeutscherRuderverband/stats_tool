########################################################################################################################
# This file contains the main procedures to initialize and update the data present in the database
#####
# Since there will only ever be one database we have to connect to, the database connection can be build in here.
########################################################################################################################

## todo: get the connection parameters from the database sub-package

import gzip
import logging
from pathlib import Path
from datetime import datetime

import sh  # shell - allows calling terminal-commands as python function. ATTENTION: THE PACKAGES HAVE TO BE INSTALLED!

from scraping_wr import api as wr

logger = logging.getLogger(__name__)

DB_BACKUP_FILE_NAME = 'pg_backup.gz'
DB_BACKUP_FOLDER_PATH = './../'
DB_BACKUP_FILE_PATH = Path(DB_BACKUP_FOLDER_PATH) / DB_BACKUP_FILE_NAME


def fetch_data(initialize: bool = False):
    """

    """
    # TODO: create connection to the database
    if initialize:
        #  The update procedure shall be triggered.
        #  This means, we only have to get data newer than out last entry
        #  So, read from the db, get the highest date occurring and read from the endpoints respectively.
        #  todo: actually, we do not have to read the db upfront, if the inserts (the keys for the respective tables)
        #   are setup correctly. See scenario:
        #  SCENARIO:
        #   A race with the id: 99, from this year - february, already exists
        #   - We ask the endpoint all the data, from this year, up to march (most recent)
        #     - as a result, we get the data, including the race with the id 99. Since the id-field in the race table
        #       is used as a PK, we can add everything we received "mindlessly".
        #   --> if done correctly, we can do the above for every entity, without having to care to much
        logger.info("INITIALIZING - All data will be aggregated.\nAggregation in progress...")
        # get all ids by not passing a year
        ids = wr.get_competition_ids()

    else:
        logger.info("UPDATING - All data will be aggregated.\nAggregation in progress...")
        # the initialization procedure shall be triggered.
        ids = wr.get_competition_ids(years=datetime.now().year)

    # get the data for the ids created above
    by_comp = wr.get_by_competition_id(comp_ids='718b3256-e778-4003-88e9-832c4aad0cc2', keys_of_interest='everything')

    print()

if __name__ == '__main__':
    ### KEEP FOR TESTING

    fetch_data()


db_settings = {
    'host': 'ip-to-db',  # can also be localhost
    'user_name': 'USERNAME',
    'db_name': 'DATABASENAME'
}


def dump():
    """
    Dump an existing postgres database to a local file
    """

    # create the path to the file, if it does not exist
    DB_BACKUP_FILE_PATH.mkdir(exist_ok=True, parents=True)

    try:
        with gzip.open(DB_BACKUP_FILE_PATH, 'wb') as file:
            # call the the shell-command pg_dump from postgress
            #  prerequisites: 'psycopg2-binary' must be installed
            sh.pg_dump('-h', db_settings['host'], '-U', db_settings['user_name'], db_settings['db_name'], _out=file)
    except Exception as e:  # no idea what we would catch here. Thus, Exception
        logger.error(f"Error during dump to local backup... \n{e}")


def restore():
    """
    Loads a postgres database from a local file
    """

    if DB_BACKUP_FILE_PATH.is_file():
        # if the file exists...
        try:
            with gzip.open(DB_BACKUP_FILE_PATH, 'r') as file:
                # call the the shell-command pg_dump from postgress
                #  prerequisites: 'psycopg2-binary' must be installed
                sh.pg_restore('-h', db_settings['host'], '-U', db_settings['user_name'], db_settings['db_name'], file)
        except Exception as e:  # no idea what we would catch here. Thus, Exception
            logger.error(f"Error during restore from local backup... \n{e}")

    else:
        logger.error(f"No file found at path: {DB_BACKUP_FILE_PATH.__str__()}")

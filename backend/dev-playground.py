# NOTE: This dev-playground.py is just for rapid testing

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import json

from scraping_wr.api import get_by_competition_id_


def grab_competition_example(competition_id, out_path='dump.json'):
    comp_data = get_by_competition_id_(comp_ids=[str(competition_id)], parse_pdf=False)
    with open(out_path, "w", encoding='ascii') as fp:
        json.dump(comp_data, fp)

if __name__ == '__main__':
    grab_competition_example('718b3256-e778-4003-88e9-832c4aad0cc2', 'tmp.competition.json')
    # The above generated JSON can be written into the database:
    #     - see model/README.md
    #     - see model.dbutils module and
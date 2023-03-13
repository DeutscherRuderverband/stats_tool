import os

DAY_IN_SECONDS = 60 * 60 * 24

# Define duration of pause after all procedures were executed
SCRAPER_SLEEP_TIME_SECONDS = 1 * DAY_IN_SECONDS

# Lower limit of competition date
SCRAPER_YEAR_MIN = int(os.environ.get('SCRAPER_YEAR_MIN', '1986').strip())

# Upper limit of competition date. (None -> unlimited)
SCRAPER_YEAR_MAX = os.environ.get('SCRAPER_YEAR_MAX', None)
SCRAPER_YEAR_MAX = int(SCRAPER_YEAR_MAX) if SCRAPER_YEAR_MAX else None

# Run all procedures only once
SCRAPER_SINGLEPASS = os.environ.get('SCRAPER_SINGLEPASS','').strip() == '1'

# Tell Scraper that it runs in dev mode
SCRAPER_DEV_MODE = os.environ.get('DRV_SCRAPER_DEV_MODE','').strip() == '1'

# Competitions older that that will not be rescraped
SCRAPER_RESCRAPE_LIMIT_DAYS = int(os.environ.get('SCRAPER_RESCRAPE_LIMIT_DAYS', '45').strip())

# Assumption on how long a competition takes
SCRAPER_MAINTENANCE_PERIOD_DAYS = int(os.environ.get('SCRAPER_MAINTENANCE_PERIOD_DAYS', '7').strip())
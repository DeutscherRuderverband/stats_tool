import os
import enum
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Float, String, Boolean, Date, DateTime, Enum

# logging stuff
import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# In-memory
# engine = create_engine("sqlite:///:memory:", echo=True)

# sqlite file relative path
# engine = create_engine("sqlite:///foo.sqlite", echo=True)

# postgres
# engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/rowing", echo=True)

# Session = sessionmaker(bind=engine)

# connect will actually establish a connection or create/load the sqlite file
# engine.connect()

"""
TODO:
    - https://worldrowing.com/event/2018-world-rowing-coastal-championships -> Has Result PDFs but not in JSON API, only in HTML
    - https://worldrowing.com/event/2021-world-rowing-final-paralympic-qualification-regatta -> same
    - Wettkampfklassen / Competition Classes

    - !!! CountryCodes are not official
    - ??? communityTypes -> U23, Senior, ...
        -> https://worldrowing.com/event/2022-world-rowing-under-23-championships
        -> https://world-rowing-api.soticcloud.net/stats/api/competition/7ee519e5-288d-4585-bab4-bf916dca49b8?include=venue,venue.country,competitionType.competitionCategory,communityTypes
        -> BEWARE: Multiple communities: https://world-rowing-api.soticcloud.net/stats/api/competition/718b3256-e778-4003-88e9-832c4aad0cc2?include=venue,venue.country,competitionType.competitionCategory,communityTypes

    - world-rowing GUIDs -> As String or Postgres UUID ?
    - race data (high res)
    - Specify Not Null Columns
    - add backref / back_populates for easy access ---> use back_populates for clean code
    - add athlete names
    - add progression string
    - Consider foreign key checking via constraints
    - Define Indexes
    - Ask DRV: Time resolution (milli, micro) !!! -> seems to be millisec -> research what res postgres' INTERVAL has
    - No data source hints are written into db (?)
    - INCLUDE PDFs!!! -> More maximalist apporach

    - Timestamp and timezones:
        https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-timestamp/
        https://codeofmatt.com/please-dont-call-it-epoch-time/#:~:text=Unix%20timestamps%20are%20always%20based,without%20any%20leaps%20ever%20occurring.

    - Query ORM Examples: https://docs.sqlalchemy.org/en/14/orm/queryguide.html#select-statements
        - Query case insensiive https://stackoverflow.com/a/47642360
https://worldrowing.com/event/2022-world-rowing-cup-iii
https://world-rowing-api.soticcloud.net/stats/api/race/?include=racePhase%2Cevent.competition.competitionType%2Cevent.competition.competitionType.competitionCategory%2Cevent.boatClass&filter%5Bevent.competitionId%5D=b56cf9a5-a7d3-4e64-9571-38218f39413b&sort%5Bdate%5D=asc

    - Efficiency of relationship fields / lazy loading:
        - https://stackoverflow.com/q/34186225
        - https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html

    - Consider BigInteger for Primary Key for races / athletes
        - Will it map to bigserial postgres type?
"""

# Provide DB objects
# ------------------

Base = declarative_base()

def get_rowing_db_url() -> str:
    """Returns URL suited for SQLAlchemy as configured by environment variables
    See: https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
    """
    db_url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
        drivername=os.environ.get('DB_SQLALCHEMY_DRIVERNAME', 'postgresql+psycopg2'),
        username=urllib.parse.quote_plus( os.environ.get('PGUSER', 'postgres') ),
        password=urllib.parse.quote_plus( os.environ.get('PGPASSWORD', 'postgres') ),
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', '5432'),
        database=os.environ.get('PGDATABASE', 'rowing')
    )
    return db_url

# NOTE: Usage pattern for flask: use scoped_session(...)
# - https://nestedsoftware.com/2018/06/11/flask-and-sqlalchemy-without-the-flask-sqlalchemy-extension-3cf8.34704.html
# - https://stackoverflow.com/questions/35664436/flask-and-sqlalchemy-handling-sessions
#     => NOTE: In case of greenlet based environment use the pattern mentioned in this
# - https://stackoverflow.com/questions/66046801/sqlalchemy-used-in-flask-session-management-implementation
# - https://towardsdatascience.com/use-flask-and-sqlalchemy-not-flask-sqlalchemy-5a64fafe22a4

__DB_URL = get_rowing_db_url()
__DB_VERBOSE = os.environ.get('DB_VERBOSITY','').strip() == '1'

engine = create_engine(__DB_URL, echo=__DB_VERBOSE)
Scoped_Session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))


# Enums
# -----
class Enum_Maintenance_Level(enum.Enum):
    """Enum for Competition Entity"""
    world_rowing_api_prescraped = 25
    world_rowing_api_scraped = 50

class Enum_Data_Provider(enum.Enum):
    manually_entered = 1
    world_rowing = 2

class Enum_Data_Source(enum.Enum):
    world_rowing_api = 1
    world_rowing_pdf = 2

# Many-To-Many Association Tables
# -------------------------------

class Association_Race_Boat_Athlete(Base):
    """Many-To-Many Pattern with extra data:
    https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
    https://stackoverflow.com/a/62378982
    
    TODO: Clean up many-to-many oprphans: https://github.com/sqlalchemy/sqlalchemy/wiki/ManyToManyOrphan"""

    __tablename__ = "association_raceboat_athlete"

    race_boat_id = Column(ForeignKey("race_boats.id", name="fk_assoc_rbta_race_boat"), primary_key=True)
    athlete_id = Column(ForeignKey("athletes.id", name="fk_assoc_rbta_athlete"), primary_key=True)

    # extra data fields
    boat_position = Column(String)

    # relationships
    race_boat = relationship("Race_Boat", back_populates="athletes")
    athlete = relationship("Athlete", back_populates="race_boats")


# ORM Classes
# -----------

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    country_code = Column(String(length=3))
    name = Column(String)

    # TODO: Clarify meaning and types
    is_former_country__ = Column(String)
    is_noc__ = Column(String)


class Venue(Base):
    """
    https://world-rowing-api.soticcloud.net/stats/api/competition/b56cf9a5-a7d3-4e64-9571-38218f39413b?include=venue,venue.country
    """
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)
    country_id = Column(ForeignKey("countries.id", name="fk_venue_country"))
    country    = relationship("Country")

    city = Column(String)
    site = Column(String)

    is_world_rowing_venue = Column(Boolean)

    # relationships
    competitions = relationship("Competition", back_populates="venue")


class Gender(Base):
    __tablename__ = "genders"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    name = Column(String)


class Athlete(Base):
    """Entity 'person' in World Rowing API"""
    __tablename__ = "athletes"

    id = Column(BigInteger, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    name = Column(String) # e.g. "KRAJANGJAM, Nuntida"
    first_name__ = Column(String) # e.g. "Nuntida"
    last_name__ = Column(String) # e.g. "KRAJANGJAM"
    birthdate = Column(Date)

    height_cm__ = Column(Integer)
    weight_kg__ = Column(Integer)

    # Country is already present at boat level
    # country_id = Column(Integer, ForeignKey("countries.id"))
    # country = relationship("Country")

    # TODO: gender? already contained in Event entity // Gender entity is not expandable in API 
    # OVRCode?

    # relationships
    race_boats = relationship("Association_Race_Boat_Athlete", back_populates="athlete")

class Boat_Class(Base):
    __tablename__ = "boat_classes"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    abbreviation = Column(String, nullable=False, unique=True)
    name = Column(String) # e.g. Lightweight Men's Quadruple Sculls // NOTE: full name not in API data

    # world best time
    world_best_race_boat_id = Column(ForeignKey("race_boats.id", name="fk_boat_class_wb_race_boat"))
    world_best_race_boat    = relationship("Race_Boat")

    # relationships
    events = relationship("Event", back_populates="boat_class")


class Competition_Type(Base):
    """https://world-rowing-api.soticcloud.net/stats/api/competition/b56cf9a5-a7d3-4e64-9571-38218f39413b/?include=competitionType,competitionType.competitionCategory"""
    __tablename__ = "competition_types"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    abbreviation = Column(String)
    name = Column(String)

    competition_category_id = Column(ForeignKey("competition_categories.id", name="fk_comp_type_comp_category"))
    competition_category    = relationship("Competition_Category", back_populates="competition_types")

    # relationships
    competitions = relationship("Competition", back_populates="competition_type")


class Competition_Category(Base):
    """https://world-rowing-api.soticcloud.net/stats/api/competition/b56cf9a5-a7d3-4e64-9571-38218f39413b/?include=competitionType,competitionType.competitionCategory"""
    __tablename__ = "competition_categories"

    id = Column(Integer, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    name = Column(String)

    # relationships
    competition_types = relationship("Competition_Type", back_populates="competition_category")


class Competition(Base):
    """https://world-rowing-api.soticcloud.net/stats/api/competition/718b3256-e778-4003-88e9-832c4aad0cc2?include=venue,competitionType"""
    __tablename__ = "competitions"

    id = Column(BigInteger, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)

    # holds info about the state of postprocessing using Enum_Maintenance_Level
    scraper_maintenance_level = Column(Integer, nullable=False)
    scraper_last_scrape = Column(DateTime)
    scraper_data_provider = Column(Integer) # Use Enum_Data_Provider

    competition_type_id = Column(ForeignKey("competition_types.id", name="fk_competition_comp_type"))
    competition_type    = relationship("Competition_Type", back_populates="competitions")
    venue_id = Column(ForeignKey("venues.id", name="fk_competition_venue"))
    venue    = relationship("Venue", back_populates="competitions")

    name = Column(String)
    year = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    is_fisa = Column(Boolean)
    competition_code__ = Column(String)

    # relationships
    events = relationship("Event", back_populates="competition")
    

class Event(Base):
    """https://world-rowing-api.soticcloud.net/stats/api/event/05ad5e77-c337-4700-bd9b-a2e0fc7e5fc2?include=boatClass"""
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)
    name = Column(String)

    competition_id = Column(ForeignKey("competitions.id", name="fk_event_competition"))
    competition    = relationship("Competition", back_populates="events")
    boat_class_id = Column(ForeignKey("boat_classes.id", name="fk_event_boat_class"))
    boat_class    = relationship("Boat_Class", back_populates="events")
    gender_id = Column(ForeignKey("genders.id", name="fk_event_gender"))
    gender    = relationship("Gender")

    rsc_code__ = Column(String) # RSC-Codes of races contain more information

    # relationships
    races = relationship("Race", back_populates="event")


class Race(Base): # https://world-rowing-api.soticcloud.net/stats/api/race/b0eae369-8d05-4b8e-9a2e-7de5871715b7?include=racePhase%2CraceBoats.raceBoatAthletes.person%2CraceBoats.invalidMarkResultCode%2CraceBoats.raceBoatIntermediates.distance&sortInclude%5BraceBoats.raceBoatIntermediates.ResultTime%5D=asc
    __tablename__ = "races"

    id = Column(BigInteger, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)
    event_id = Column(ForeignKey("events.id", name="fk_race_event"))
    event    = relationship("Event", back_populates="races")

    name = Column(String)
    date = Column(DateTime)

    phase_type = Column(String) # e.g. "heat", "final", "semifinal"
    phase_subtype = Column(String) # e.g. "SA/B/C 1" -> "A/B/C", "FB" -> NULL, "H3" -> NULL
    phase_number = Column(Integer) # e.g. "SA/B/C 1" -> 1, "FB" -> 2, "H3" -> 3

    progression = Column(String) # e.g. "1-2->SA/B, 3..->R"
    rsc_code = Column(String)

    # To be able to filter for standard 2000m races // inferred by year threshold
    # NOTE: Consider to hold this info at event or even competition level
    # course_length = Column(Integer, index=True) # assumed 2km for all data existing in database
    
    pdf_url_results = Column(String)
    pdf_url_race_data = Column(String)

    # course_length_meter = Column(Integer) # e.g. 2000 for 2000 meter course # Hypothesis: Competition.is_fisa -> 2000m ? TODO: data exploration

    # Meaning and importance not exactly clear
    race_nr__ = Column(String) # e.g. "103"
    rescheduled__ = Column(String) # e.g. 0 # maybe map to bool?
    rescheduled_from__ = Column(String) # low-prio TODO: Type unclear
    race_status__ = Column(String) # e.g. DisplayName "Official" id "182f6f15-8e78-41c3-95b3-8b006af2c6a1"

    # relationships
    race_boats = relationship("Race_Boat", back_populates="race")


class Invalid_Mark_Result_Code(Base):
    __tablename__ = "invalid_mark_result_codes"

    id = Column(String, primary_key=True)
    name = Column(String)


class Race_Boat(Base):
    '''
    Boat vs RaceBoat
    For each "Race" a "Boat" participates in, a "Race Boat" entity is created.
    Thus, a "Boat" holds final rank, while "Race Boat" holds the rank of the assigned "Race".
    In World Rowing API a "Boat" is assigned to an "Event".
    ===> TODO: Consider to implement this in the database model.
    '''
    __tablename__ = "race_boats"

    id = Column(BigInteger, primary_key=True)
    additional_id_ = Column(String, index=True, unique=True)
    race_id = Column(ForeignKey("races.id", name="fk_race_boat_race"))
    race    = relationship("Race", back_populates="race_boats")
    country_id = Column(ForeignKey("countries.id", name="fk_race_boat_country"))
    country    = relationship("Country")

    # many-to-many relationship
    athletes = relationship("Association_Race_Boat_Athlete", back_populates="race_boat", cascade='all,delete,delete-orphan')

    name = Column(String) # e.g. "GER2" for one of the German boats

    # Result time for this race. It should be null, if the race was invalid for this boat.
    result_time_ms = Column(Integer, nullable=True) # milliseconds as Integer

    # If race was invalid, this field should provide the reason.
    # E.g. "DNS" Did not start; "BUW" Boat under weight, etc.
    invalid_mark_result_code_id = Column(ForeignKey("invalid_mark_result_codes.id", name="fk_race_boat_invalid_mark_result_code"))
    invalid_mark_result_code    = relationship("Invalid_Mark_Result_Code")

    lane = Column(Integer) # e.g. 1
    rank = Column(Integer) # e.g. 2

    # TODO: Meaning, importance and/or type unclear
    remark__ = Column(String)
    world_cup_points__ = Column(Integer)
    club_name__ = Column(String)
    # worldBestTimeId, OVRCode ?

    # relationships
    intermediates = relationship("Intermediate_Time", back_populates="race_boat", cascade='all,delete,delete-orphan')
    race_data = relationship("Race_Data", back_populates="race_boat", cascade='all,delete,delete-orphan')

    # NOTE:
    #     (X) invalidMarkResultCode => DNS, DNF, BUW, etc (Foreign Key? or second field for long name?)
    #     (X) result_time (null in case of invalidMarkResultCode != null)
    #           ===> Alternatively, Put it in Intermediates with a bool field marking it "finish_time";
    #                Since the other approach is kind of denormalized.

class Race_Data(Base):
    __tablename__ = "race_data"

    # Multi Column Primary Key: https://stackoverflow.com/a/9036128
    race_boat_id = Column(BigInteger, ForeignKey("race_boats.id", name="fk_race_data_race_boat"), primary_key=True, autoincrement=False)
    race_boat    = relationship("Race_Boat", back_populates="race_data")
    distance_meter = Column(Integer, primary_key=True, autoincrement=False)

    data_source = Column(Integer) # Use Enum_Data_Source class

    # Data fields from race data PDFs
    speed_meter_per_sec = Column(Float)
    stroke = Column(Float)

    # outlier detection
    is_outlier = Column(Boolean, nullable=False, default=True)


class Intermediate_Time(Base):
    __tablename__ = "intermediate_times"

    # Multi Column Primary Key: https://stackoverflow.com/a/9036128
    race_boat_id = Column(ForeignKey("race_boats.id", name="fk_intermediate_time_race_boat"), primary_key=True, autoincrement=False)
    race_boat    = relationship("Race_Boat", back_populates="intermediates")
    distance_meter = Column(Integer, primary_key=True, autoincrement=False)

    data_source = Column(Integer) # Use Enum_Data_Source class

    # E.g. "DNS" Did not start; "BUW" Boat under weight, etc.
    invalid_mark_result_code_id = Column(ForeignKey("invalid_mark_result_codes.id", name="fk_intermediate_time_invalid_mark_result_code"))
    invalid_mark_result_code    = relationship("Invalid_Mark_Result_Code")

    # Data fields from JSON Web API aka "Intermediates"
    rank = Column(Integer)
    result_time_ms = Column(Integer) # in milliseconds // TODO: as String?

    # outlier detection
    is_outlier = Column(Boolean, nullable=False, default=True)

    # other wr API fields
    start_position__ = Column(String)


#----------------------------------------------------------------------


if __name__ == '__main__':
    # Problem with PYTHONPATH vs CWD/PWD: https://stackoverflow.com/a/24435742
    from sys import path as syspath
    print("PYTHONPATH", syspath[0])
    # import backend.scraping_wr.api

    # solution: run as module `python -m backend.model.model`
    # from .. scraping_wr import api
    # print("api", api)

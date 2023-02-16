from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema

from datetime import datetime

@dataclass
class DC_Race(DC_Schema):
    #  ID PRESENT IN DC_Schema
    display_name: str
    rescheduled_from: datetime.date
    rescheduled: bool
    rsc_code: str
    pdf_url_result: str
    pdf_url_race_data: str
    is_started: bool
    race_phase: str
    progression: str
    date: datetime.date

    def __init__(self, _id: str,
                 display_name: str,
                 rescheduled_from: datetime.date, rescheduled: bool,
                 rsc_code: str, pdf_url_result: str,
                 pdf_url_race_data: str, is_started: bool,
                 race_phase: str, progression: str,
                 date: datetime.date):

        self.display_name = display_name
        self.rescheduled_from = rescheduled_from
        self.rescheduled = rescheduled
        self.rsc_code = rsc_code
        self.pdf_url_result = pdf_url_result
        self.pdf_url_race_data = pdf_url_race_data
        self.is_started = is_started
        self.race_phase = race_phase
        self.progression = progression
        self.date = date

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

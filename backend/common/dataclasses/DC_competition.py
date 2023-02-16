from dataclasses import dataclass
from datetime import datetime
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Competition(DC_Schema):
    #  ID PRESENT IN DC_Schema
    comp_code: str
    display_name: str
    start_date: datetime.date
    end_date: datetime.date
    year: int
    is_fisa: bool
    has_result: bool

    def __init__(
            self, _id: str,
            comp_code: str, display_name: str,
            start_date: datetime.date, end_date: datetime.date,
            year: int, is_fisa: bool, has_result: bool):

        self.comp_code = comp_code
        self.display_name = display_name
        self.start_date = start_date
        self.end_date = end_date
        self.year = year
        self.is_fisa = is_fisa
        self.has_result = has_result

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

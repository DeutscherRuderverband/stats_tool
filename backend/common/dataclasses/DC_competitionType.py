from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_CompetitionType(DC_Schema):
    #  ID PRESENT IN DC_Schema
    abbreviation: str
    display_name: str

    def __init__(self, _id: str, abbreviation: str, display_name: str):
        self.abbreviation = abbreviation
        self.display_name = display_name

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

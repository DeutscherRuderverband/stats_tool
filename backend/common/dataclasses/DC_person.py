from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Person(DC_Schema):
    #  ID PRESENT IN DC_Schema
    first_name: str
    last_name: str
    display_name: str

    def __init__(self, _id: str, first_name: str, last_name: str, display_name: str):
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

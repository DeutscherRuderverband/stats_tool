import logging
from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Boat(DC_Schema):
    #  ID PRESENT IN DC_Schema
    type: str
    display_name: str

    def __init__(self, _id: str, _type: str, display_name: str):
        self.type = _type
        self.display_name = display_name

        super().__init__(_id=_id)

    def __post__init__(self):
        print("hallo from the post init")
        pass

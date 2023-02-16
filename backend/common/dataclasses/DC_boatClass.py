from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_BoatClass(DC_Schema):
    #  ID PRESENT IN DC_Schema
    order: int
    display_name: str

    def __init__(self, _id: str, _type: str):
        self.type = _type

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

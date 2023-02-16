from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Event(DC_Schema):
    #  ID PRESENT IN DC_Schema
    display_name: str
    rsc_code: str

    def __init__(self, _id: str, display_name: str, rsc_code: str):
        self.display_name = display_name
        self.rsc_code = rsc_code

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

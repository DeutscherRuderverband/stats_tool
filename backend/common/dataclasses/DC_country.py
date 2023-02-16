from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Country(DC_Schema):
    #  ID PRESENT IN DC_Schema
    display_name: str
    country_code: str
    is_former_country: bool
    is_noc: bool

    def __init__(self, _id: str, display_name: str, country_code: str, is_former_country: bool, is_noc: bool):
        self.display_name = display_name
        self.country_code = country_code
        self.is_former_country = is_former_country
        self.is_noc = is_noc

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

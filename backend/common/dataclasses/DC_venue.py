from dataclasses import dataclass
import typing

from .DC_Schema import DC_Schema


@dataclass
class DC_Venue(DC_Schema):
    #  ID PRESENT IN DC_Schema
    display_name: str
    is_world_rowing_venue: bool
    region_city: str
    site: str

    def __init__(self, _id: str, display_name: str, is_world_rowing_venue: bool, region_city: str, site: str):
        self.display_name = display_name
        self.is_world_rowing_venue = is_world_rowing_venue
        self.region_city = region_city
        self.site = site

        super().__init__(_id=_id)

    def __post__init__(self):
        pass

# imports
import os
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = '1' # Suppress sqlalchemy warning

from database import session
from variables import DATE_FROM, DATE_TO
from model import (Race_Data, Race, Race_Boat, Intermediate_Time, Athlete, Association_Race_Boat_Athlete,
                    Event, Competition, Country, Gender, Competition_Type, Venue, Boat_Class)

import pandas as pd
from sqlalchemy import select, func
from sqlalchemy import case, select, func
from sqlalchemy.dialects.postgresql import aggregate_order_by
import re

# DATENBANKABFRAGE
print("Starte den Datenbank-Export...")

# Subquery für Stroke Rate
stroke_rate = (
    select(
        Race_Data.race_boat_id.label("boat_id"),
        func.avg(case((Race_Data.distance_meter.between(50, 500), Race_Data.stroke))).label("stroke_500"),  #500 m
        func.avg(case((Race_Data.distance_meter.between(550, 1000), Race_Data.stroke))).label("stroke_1000"),  #1000 m
        func.avg(case((Race_Data.distance_meter.between(1050, 1500), Race_Data.stroke))).label("stroke_1500"),  #1500 m
        func.avg(case((Race_Data.distance_meter.between(1550, 2000), Race_Data.stroke))).label("stroke_2000")  #2000 m
    )
    .group_by(Race_Data.race_boat_id)
    .subquery()
) 

# Subquery für die Fahrzeiten der Plätze 1-3 in Finale A
finale_a_times = (
    select(
        Race.event_id,
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 1).label("Fahrzeit_Gold"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 2).label("Fahrzeit_Silber"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 3).label("Fahrzeit_Bronze"),
        
        # 🏁 Intermediate times at 500m, 1000m, 1500m, 2000m for Final A
        func.min(case((Intermediate_Time.distance_meter == 500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 1).label("split_500_gold"),
        func.min(case((Intermediate_Time.distance_meter == 1000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 1).label("split_1000_gold"),
        func.min(case((Intermediate_Time.distance_meter == 1500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 1).label("split_1500_gold"),
        func.min(case((Intermediate_Time.distance_meter == 2000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 1).label("split_2000_gold"),

        func.min(case((Intermediate_Time.distance_meter == 500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 2).label("split_500_silver"),
        func.min(case((Intermediate_Time.distance_meter == 1000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 2).label("split_1000_silver"),
        func.min(case((Intermediate_Time.distance_meter == 1500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 2).label("split_1500_silver"),
        func.min(case((Intermediate_Time.distance_meter == 2000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 2).label("split_2000_silver"),

        func.min(case((Intermediate_Time.distance_meter == 500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 3).label("split_500_bronze"),
        func.min(case((Intermediate_Time.distance_meter == 1000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 3).label("split_1000_bronze"),
        func.min(case((Intermediate_Time.distance_meter == 1500, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 3).label("split_1500_bronze"),
        func.min(case((Intermediate_Time.distance_meter == 2000, Intermediate_Time.result_time_ms))).filter(Race_Boat.rank == 3).label("split_2000_bronze"),
 
         # 🏁 Stroke-Rate für 500m, 1000m, 1500m, 2000m für Platz 1-3
        func.min(stroke_rate.c.stroke_500).filter(Race_Boat.rank == 1).label("stroke_500_gold"),
        func.min(stroke_rate.c.stroke_1000).filter(Race_Boat.rank == 1).label("stroke_1000_gold"),
        func.min(stroke_rate.c.stroke_1500).filter(Race_Boat.rank == 1).label("stroke_1500_gold"),
        func.min(stroke_rate.c.stroke_2000).filter(Race_Boat.rank == 1).label("stroke_2000_gold"),

        func.min(stroke_rate.c.stroke_500).filter(Race_Boat.rank == 2).label("stroke_500_silver"),
        func.min(stroke_rate.c.stroke_1000).filter(Race_Boat.rank == 2).label("stroke_1000_silver"),
        func.min(stroke_rate.c.stroke_1500).filter(Race_Boat.rank == 2).label("stroke_1500_silver"),
        func.min(stroke_rate.c.stroke_2000).filter(Race_Boat.rank == 2).label("stroke_2000_silver"),

        func.min(stroke_rate.c.stroke_500).filter(Race_Boat.rank == 3).label("stroke_500_bronze"),
        func.min(stroke_rate.c.stroke_1000).filter(Race_Boat.rank == 3).label("stroke_1000_bronze"),
        func.min(stroke_rate.c.stroke_1500).filter(Race_Boat.rank == 3).label("stroke_1500_bronze"),
        func.min(stroke_rate.c.stroke_2000).filter(Race_Boat.rank == 3).label("stroke_2000_bronze")
    
    
    
    )
    .join(Intermediate_Time, Intermediate_Time.race_boat_id == Race_Boat.id, isouter=True)
    .join(stroke_rate, stroke_rate.c.boat_id == Race_Boat.id, isouter=True) # Outer join so data gets included also if there is no stroke data available
    .join(Race_Boat.race)
    .where(
        Race.phase_type == "final",
        Race.phase_number == 1
    )  # Finale A explizit filtern!
    .group_by(Race.event_id)
    .subquery()
)

# Subquery: Get race-wide times for places 1-6
race_wide_times = (
    select(
        Race.id.label("race_id"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 1).label("Fahrzeit_Platz1"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 2).label("Fahrzeit_Platz2"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 3).label("Fahrzeit_Platz3"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 4).label("Fahrzeit_Platz4"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 5).label("Fahrzeit_Platz5"),
        func.min(Race_Boat.result_time_ms).filter(Race_Boat.rank == 6).label("Fahrzeit_Platz6")
    )
    .join(Race_Boat.race)
    .group_by(Race.id)
    .subquery()
)


# Subquery for athletes
athletes = (
    select(
        Race_Boat.id.label("race_boat_id"),
        func.string_agg(
            Athlete.name,
            aggregate_order_by('; ', case(
                    [
                        (Association_Race_Boat_Athlete.boat_position.like('b%'), '1'),  # 'b' -> 1
                        (Association_Race_Boat_Athlete.boat_position.like('s%'), '8'),  # 's' -> 8
                        (Association_Race_Boat_Athlete.boat_position.like('c%'), '9'),  # 'c' -> 9
                    ],
                    else_=Association_Race_Boat_Athlete.boat_position  # Keep original value for others
                ))).label("Mannschaft")
    )
    .join(Association_Race_Boat_Athlete.race_boat)
    .join(Association_Race_Boat_Athlete.athlete)
    .join(Race_Boat.race)
    .join(Race.event)
    .join(Event.competition)
    .join(Competition.competition_type)
    .group_by(Race_Boat.id)
    .subquery()
)

# Subquery for Intermediates
intermediates = (
    select(
        Intermediate_Time.race_boat_id,  # Group by race_boat_id
        func.max(case((Intermediate_Time.distance_meter == 500, Intermediate_Time.result_time_ms))).label("split_500"),
        func.max(case((Intermediate_Time.distance_meter == 1000, Intermediate_Time.result_time_ms))).label("split_1000"),
        func.max(case((Intermediate_Time.distance_meter == 1500, Intermediate_Time.result_time_ms))).label("split_1500"),
        func.max(case((Intermediate_Time.distance_meter == 2000, Intermediate_Time.result_time_ms))).label("split_2000"),
    )
    .group_by(Intermediate_Time.race_boat_id)  # Ensures one row per race_boat_id
    .subquery()
)




statement = (
        select(
            Country.country_code.label("Nation"),
            Athlete.first_name__.label("Vorname"),
            Athlete.last_name__.label("Name"),
            Athlete.birthdate.label("Geburtsdatum"),
            Gender.name.label("Geschlecht"),
            Competition_Type.name.label("Wettbewerb"),
            Race.date.label("Datum"),
            Venue.city.label("Ort"),
            Boat_Class.abbreviation.label("Bootsklasse"),
            Race.phase_type.label("Lauf"),
            Race.phase_number.label("Laufnummer"),
            Race.phase_subtype.label("Lauftyp"),
            Race_Boat.rank.label("Platz"),
            Race_Boat.id.label("race_boat_id"),
            Race_Boat.result_time_ms.label("Fahrzeit"),
            Race.id.label("race_id"),
            Race.progression.label("Progression"),
            
             # Intermediate times from the subquery
            intermediates.c.split_500,
            intermediates.c.split_1000,
            intermediates.c.split_1500,
            intermediates.c.split_2000,
            
            # Stroke Rate
            stroke_rate.c.stroke_500,
            stroke_rate.c.stroke_1000,
            stroke_rate.c.stroke_1500,
            stroke_rate.c.stroke_2000,
            
            
            # Final A values
            finale_a_times.c.Fahrzeit_Gold,
            finale_a_times.c.Fahrzeit_Silber,
            finale_a_times.c.Fahrzeit_Bronze,
            finale_a_times.c.split_500_gold,
            finale_a_times.c.split_1000_gold,
            finale_a_times.c.split_1500_gold,
            finale_a_times.c.split_2000_gold,
            finale_a_times.c.split_500_silver,
            finale_a_times.c.split_1000_silver,
            finale_a_times.c.split_1500_silver,
            finale_a_times.c.split_2000_silver,
            finale_a_times.c.split_500_bronze,
            finale_a_times.c.split_1000_bronze,
            finale_a_times.c.split_1500_bronze,
            finale_a_times.c.split_2000_bronze,
            
            finale_a_times.c.stroke_500_gold,
            finale_a_times.c.stroke_1000_gold,
            finale_a_times.c.stroke_1500_gold,
            finale_a_times.c.stroke_2000_gold,
            finale_a_times.c.stroke_500_silver,
            finale_a_times.c.stroke_1000_silver,
            finale_a_times.c.stroke_1500_silver,
            finale_a_times.c.stroke_2000_silver,
            finale_a_times.c.stroke_500_bronze,
            finale_a_times.c.stroke_1000_bronze,
            finale_a_times.c.stroke_1500_bronze,
            finale_a_times.c.stroke_2000_bronze,
            
            # Race times
            race_wide_times.c.Fahrzeit_Platz1,
            race_wide_times.c.Fahrzeit_Platz2,
            race_wide_times.c.Fahrzeit_Platz3,
            race_wide_times.c.Fahrzeit_Platz4,
            race_wide_times.c.Fahrzeit_Platz5,
            race_wide_times.c.Fahrzeit_Platz6,
            
            # Athletes
            athletes.c.Mannschaft
            
            
        )
        .join(Association_Race_Boat_Athlete.race_boat)
        .join(Association_Race_Boat_Athlete.athlete)
        .join(Race_Boat.race)
        .join(Race_Boat.country)
        .join(Race.event)
        .join(Event.competition)
        .join(Event.gender)
        .join(Event.boat_class)
        .join(Competition.competition_type)
        .join(Competition.venue)
        .outerjoin(stroke_rate, stroke_rate.c.boat_id == Race_Boat.id)
        .outerjoin(race_wide_times, race_wide_times.c.race_id == Race.id)
        .outerjoin(finale_a_times, finale_a_times.c.event_id == Event.id)
        .outerjoin(athletes, athletes.c.race_boat_id == Race_Boat.id)
        .outerjoin(intermediates, intermediates.c.race_boat_id == Race_Boat.id)
        .where(
            Competition_Type.abbreviation.in_(["WCH","WCp 1", "WCp 2", "WCp 3", "ECH", "OG", "U23WCH", "JWCH", "ERU23CH",
                                               "EJCH", "WRU19U23CH", "WRSU23U19CH"]),
            Race.date.between(DATE_FROM, DATE_TO)
        )
    )

data = session.execute(statement)
rows = data.mappings().all()
data_df = pd.DataFrame(rows)
print("Daten erfolgreich aus der Datenbank geladen.")
column_order = ["Nation", "Name", "Vorname", "Geburtsdatum", "Geschlecht", "Wettbewerb", "Datum", "Ort", "Bootsklasse",
                "Mannschaft", "Lauf",  "Lauftyp", "Laufnummer", "Platz", "Fahrzeit",
                "Fahrzeit_Gold", "Fahrzeit_Silber", "Fahrzeit_Bronze",
                "Fahrzeit_Platz1", "Fahrzeit_Platz2", "Fahrzeit_Platz3", "Fahrzeit_Platz4", "Fahrzeit_Platz5", "Fahrzeit_Platz6",
                "split_500", "split_1000", "split_1500", "split_2000",
                "stroke_500", "stroke_1000", "stroke_1500", "stroke_2000",
                "split_500_gold", "split_1000_gold", "split_1500_gold", "split_2000_gold",
                "stroke_500_gold", "stroke_1000_gold", "stroke_1500_gold", "stroke_2000_gold",
                "split_500_silver", "split_1000_silver", "split_1500_silver", "split_2000_silver",
                "stroke_500_silver", "stroke_1000_silver", "stroke_1500_silver", "stroke_2000_silver",
                "split_500_bronze", "split_1000_bronze", "split_1500_bronze", "split_2000_bronze",
                "stroke_500_bronze", "stroke_1000_bronze", "stroke_1500_bronze", "stroke_2000_bronze", "Progression"]
data_df = data_df[column_order]


# Formatierung der Daten

# Separate table for wbt
statement = (
select(
    Race_Boat.result_time_ms.label("Bestzeit"),
    Boat_Class.abbreviation.label("Bootsklasse")
)
    .join(Boat_Class.world_best_race_boat)
) 

data = session.execute(statement)
rows = data.mappings().all()
wbt_df = pd.DataFrame(rows)

def format_time(ms):
    if pd.isna(ms) or ms == "" or ms == 0:  # Prüft auf NaN oder leere Werte
        return ""  # Gibt eine leere Zeichenkette zurück
    try:
        ms = int(float(ms))  # Sicherstellen, dass ms eine Zahl ist
        minutes = ms // 60000  # Ganze Minuten
        seconds = (ms % 60000) // 1000  # Ganze Sekunden
        milliseconds = ms % 1000  # Millisekunden
        return f"{minutes:02}:{seconds:02},{milliseconds:01}"  # Format mm:ss,ms
    except ValueError:
        return ""  # Falls Konvertierung fehlschlägt, leer lassen
    
def get_wbt(boatclass):
    boatclass = re.sub(r'^[BJ](?=\w)', '', boatclass)
    besttime = wbt_df.loc[wbt_df["Bootsklasse"] == boatclass, "Bestzeit"]
    return next(iter(besttime), None)

data_df["Name"] = data_df["Name"].str.title()
data_df["Mannschaft"] = data_df["Mannschaft"].str.title()
data_df["Datum"] = pd.to_datetime(data_df["Datum"], errors='coerce')
data_df.insert(data_df.columns.get_loc('Datum') + 1, "Uhrzeit", data_df["Datum"].dt.time)
data_df["Datum"] = data_df["Datum"].dt.date
data_df.insert(data_df.columns.get_loc("Progression"), "Relationszeit", data_df["Bootsklasse"].apply(get_wbt))
     
    
time_columns = ["Fahrzeit", "Relationszeit", "Fahrzeit_Platz1", "Fahrzeit_Platz2", "Fahrzeit_Platz3", "Fahrzeit_Platz4", "Fahrzeit_Platz5", "Fahrzeit_Platz6", "Fahrzeit_Gold", "Fahrzeit_Silber", "Fahrzeit_Bronze", "split_500", "split_1000", "split_1500", "split_2000", "split_500_gold", "split_1000_gold", "split_1500_gold", "split_2000_gold",
"split_500_silver", "split_1000_silver", "split_1500_silver", "split_2000_silver",
"split_500_bronze", "split_1000_bronze", "split_1500_bronze", "split_2000_bronze"]

for col in time_columns:
    data_df[col] = data_df[col].apply(format_time)
    
    
data_df = data_df.round(1)
data_df["Platz"] = data_df["Platz"].fillna(0).round(0).astype(int)

filename = f"../Renndaten_{DATE_FROM.strftime('%Y-%m-%d')}_bis_{DATE_TO.strftime('%Y-%m-%d')}.xlsx"
data_df.to_excel(filename, index=False)
print("Daten in Excel gespeichert")
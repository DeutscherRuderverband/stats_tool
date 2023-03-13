# Database Model Notes

## Command line helpers

Create tables

    python -m model.dbutils --create

Drop tables

    python -m model.dbutils --drop

Insert a rowing competition from JSON file (World Rowing API Data Structure).

    python -m model.dbutils --insert competition.json

See *[/doc/examples/competition.json](/doc/examples/competition.json)* for an example JSON file. That can be inserted.
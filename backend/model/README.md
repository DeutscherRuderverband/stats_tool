# Database Model Notes

## Command line helpers

Create tables

    python -m model.dbutils --create

Drop tables

    python -m model.dbutils --drop

Insert a rowing competition from JSON file (World ROwing API Data Structure)

    python -m model.dbutils --insert competition.json
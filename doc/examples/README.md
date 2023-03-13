## competition.json

This is an example of a competition JSON as provided by the World Rowing API. It was grabbed using `get_by_competition_id_()` from the `scraping_wr.api` module.

The function creates an API call that looks like the following URL (for competition with the id `718b3256-e778-4003-88e9-832c4aad0cc2`):

```
https://world-rowing-api.soticcloud.net/stats/api/competition/718b3256-e778-4003-88e9-832c4aad0cc2?include=competitionType,competitionType.competitionCategory,venue,venue.country,events.gender,events.boatClass,events.pdfUrls,events.races,events.races.raceStatus,events.races.racePhase,events.races.raceBoats.boat,events.races.raceBoats.invalidMarkResultCode,events.races.raceBoats.country,events.races.raceBoats.raceBoatAthletes.person,events.races.raceBoats.raceBoatAthletes.person.country,events.races.raceBoats.raceBoatIntermediates.distance,events.races.pdfUrls.orisCode,pdfUrls.orisCode
```

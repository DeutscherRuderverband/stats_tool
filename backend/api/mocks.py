def mock_race_analysis_endpoint() -> list[dict]:
    mock = [
        {
            "raceId": 195638,
            "displayName": "Men's Eight Heat 1",
            "startDate": "2022-06-16 14:12:00",
            "venue": "Malta/Poznan, Poland",
            "boatClass": "Men's Eight",
            "worldBestTimeBoatClass": "00:05:58,36",
            "bestTimeBoatClassCurrentOZ": "00:05:58,36",
            "data": [
                {
                    "nationIoc": "CZE",
                    "nationDisplayName": "Tschechien",
                    "lane": 2,
                    "rank": 1,
                    "run": "FB",
                    "progressionCode": "1-3SA/B 4..SC/D",
                    "athletes": [
                        {
                            "id": 98245435,
                            "firstName": "Lukas",
                            "lastName": "Helesic"
                        },
                        {
                            "id": 954345365,
                            "firstName": "S Jakub",
                            "lastName": "Podrazil"
                        }
                    ],
                    "intermediates": {
                        "500": {
                            "time": "00:02:24,12",
                            "pace": "00:02:24,12",
                            "rank": 2,
                            "deficit": "00:00:03,12",
                            "relDiffToAvgSpeed": -1.3
                        },
                        "1000": {
                            "time": "00:03:13,82",
                            "pace": "00:01:50,72",
                            "rank": 1,
                            "deficit": "00:00:00,00",
                            "relDiffToAvgSpeed": 4.3
                        },
                        "1500": {
                            "time": "00:04:52,00",
                            "pace": "00:01:50,72",
                            "rank": 1,
                            "deficit": "00:00:00,00",
                            "relDiffToAvgSpeed": 2.3
                        },
                        "2000": {
                            "time": "00:06:29,14",
                            "pace": "00:01:50,72",
                            "rank": 1,
                            "deficit": "00:00:00,00",
                            "relDiffToAvgSpeed": 1.3
                        }
                    },
                    "gpsData": {
                        "distance": {
                            "50": {
                                "speed": 5.2,
                                "stroke": 34.1,
                                "propulsion": 8.3
                            },
                            "100": {
                                "speed": 4.9,
                                "stroke": 33.4,
                                "propulsion": 8.8
                            },
                            "150": {
                                "speed": 4.7,
                                "stroke": 35.0,
                                "propulsion": 7.1
                            },
                            "200": {
                                "speed": 4.6,
                                "stroke": 38.0,
                                "propulsion": 8.1
                            },
                            "250": {
                                "speed": 4.9,
                                "stroke": 32.0,
                                "propulsion": 7.2
                            }
                        }
                    }
                }
            ]
        },
    ]
    return mock


def mock_standard_analysis_endpoint() -> list[dict]:
    mock = [
        {
            "id": 395871,
            "display_name": "2022 World Rowing Cup II",
            "venue": "Malta/Poznan, Poland",
            "start_date": "2022-06-16 00:00:00",
            "competition_category": "World Rowing Cup",
            "events": [
                {
                    "id": 734839,
                    "display_name": "Lightweight Women's Single Sculls",
                    "races": [
                        {"id": 187573, "display_name": "Final FB"},
                        {"id": 424754, "display_name": "Heat 1"}
                    ]
                },
                {
                    "id": 748394,
                    "display_name": "Men's Four",
                    "races": [
                        {"id": 195638, "display_name": "Men's Eight Heat 1"},
                        {"id": 823759, "display_name": "Men's Eight Final FA"},
                        {"id": 748394, "display_name": "Men's Eight Repechage"},
                        {"id": 839473, "display_name": "Men's Eight Heat 2"}
                    ]
                }
            ]
        },
        {
            "id": 123456,
            "display_name": "2021 World Rowing Cup I",
            "venue": "Somecity, Someland",
            "start_date": "2022-06-16 00:00:00",
            "competition_category": "World Rowing Cup",
            "events": [
                {
                    "id": 234567,
                    "display_name": "Lightweight Women's Single Sculls",
                    "races": [
                        {"id": 345678, "display_name": "Semi-Final FB"},
                        {"id": 456789, "display_name": "Heat Repechage"}
                    ]
                },
                {
                    "id": 567891,
                    "display_name": "Men's Four",
                    "races": [
                        {"id": 678910, "display_name": "Women's Eight Heat 1"},
                        {"id": 789101, "display_name": "Women's Eight Final FA"},
                        {"id": 891011, "display_name": "Women's Eight Repechage"},
                        {"id": 910111, "display_name": "Women's Eight Heat 2"}
                    ]
                }
            ]
        }
    ]
    return mock

def generic_get_data(_filter: dict, is_outer_filter: bool = True) -> dict:
    """
    TODO 0: Access the database through some connection and aggregate the data resulting from the passed _filter.
    @param _filter: dict - A dictionary defining filter-criteria for the resulting data.
    @return: data - dict:  The requested data, according to the _filter. The result can be nested
    """
    data = { "_filter": _filter }
    return data
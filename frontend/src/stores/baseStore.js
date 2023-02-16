import axios from "axios";
import {defineStore} from "pinia";

// function to convert milliseconds to min:sec:ms
const formatMilliseconds = ms => {
    if (!ms) {
        return '00:00.000';
    }
    return new Date(ms).toISOString().slice(14, -2);
};


// predefined colors for charts
const COLORS = ['#0C67F7', '#93E9ED', '#E0A9FA', '#E0B696', '#E0FAAC', '#F0E95A'];

export const useRennstrukturAnalyseState = defineStore({
    id: "base",
    state: () => ({
        filterOpen: false,
        loadingState: false,
        tableExport: [],
        data: {
            filterOptions: [{
                // TODO: Year also has to be defined by backend data
                "year": [{"start_year": 1950}, {"end_year": 2025}],
                "competition_category_ids": []
            }],
            raceData: [{
                "race_id": 2841,
                "display_name": "FA",
                "start_date": "2019-07-13 16:15:00",
                "venue": "None/Rotterdam, Netherlands",
                "boat_class": "LM2-",
                "result_time_world_best": null,
                "result_time_best_of_current_olympia_cycle": 407360.0,
                "progression_code": null,
                "pdf_urls": {
                    "result": "https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/WCp3_2019_1/WCP3_2019_1_ROWMNOCOX2-L----------FNL-000100--_C73X2971.PDF",
                    "race_data": "https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/WCp3_2019_1/WCP3_2019_1_ROWMNOCOX2-L----------FNL-000100--_C77X2526.PDF"
                },
                "race_boats": [{
                    "name": "CZE",
                    "lane": 1,
                    "rank": 1,
                    "athletes": [{
                        "id": 1750,
                        "first_name": "Jiri",
                        "last_name": "KOPAC",
                        "full_name": "KOPAC, Jiri",
                        "boat_position": "b"
                    }, {
                        "id": 2634,
                        "first_name": "Jan",
                        "last_name": "HAJEK",
                        "full_name": "HAJEK, Jan",
                        "boat_position": "s"
                    }],
                    "intermediates": {
                        "500": {
                            "rank": 1,
                            "time [millis]": 112000,
                            "pace [millis]": 112000,
                            "speed [m/s]": 4.464285714285714,
                            "deficit [millis]": 0,
                            "rel_diff_to_avg_speed [%]": 3.233786203700001
                        },
                        "1000": {
                            "rank": 1,
                            "time [millis]": 228000,
                            "pace [millis]": 116000,
                            "speed [m/s]": 4.310344827586207,
                            "deficit [millis]": 0,
                            "rel_diff_to_avg_speed [%]": 4.018052531958565
                        },
                        "1500": {
                            "rank": 1,
                            "time [millis]": 347000,
                            "pace [millis]": 119000,
                            "speed [m/s]": 4.201680672268908,
                            "deficit [millis]": 0,
                            "rel_diff_to_avg_speed [%]": 1.2552301255230291
                        }
                    },
                    "race_data": {
                        "50": {"speed [m/s]": 4.7, "stroke [1/min]": 43.0, "propulsion [m/stroke]": 6.558139534883721},
                        "100": {"speed [m/s]": 4.9, "stroke [1/min]": 41.0, "propulsion [m/stroke]": 7.170731707317073},
                        "150": {"speed [m/s]": 4.7, "stroke [1/min]": 39.0, "propulsion [m/stroke]": 7.230769230769231},
                        "200": {
                            "speed [m/s]": 4.6,
                            "stroke [1/min]": 38.0,
                            "propulsion [m/stroke]": 7.2631578947368425
                        },
                        "250": {"speed [m/s]": 4.5, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 7.297297297297297},
                        "300": {"speed [m/s]": 4.5, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 7.297297297297297},
                        "350": {"speed [m/s]": 4.5, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 7.297297297297297},
                        "400": {"speed [m/s]": 4.5, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.5},
                        "450": {"speed [m/s]": 4.4, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.542857142857143},
                        "500": {"speed [m/s]": 4.5, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.5},
                        "550": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "600": {"speed [m/s]": 4.3, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.371428571428571},
                        "650": {"speed [m/s]": 4.4, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.542857142857143},
                        "700": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "750": {"speed [m/s]": 4.4, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.333333333333333},
                        "800": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "850": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "900": {"speed [m/s]": 4.3, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.371428571428571},
                        "950": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1000": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1050": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.028571428571428
                        },
                        "1100": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.411764705882353
                        },
                        "1150": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1200": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1250": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1300": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1350": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1400": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1450": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1500": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1550": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1600": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1650": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1700": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1750": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1800": {
                            "speed [m/s]": 4.4,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.542857142857143
                        },
                        "1850": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1900": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 7.166666666666667
                        },
                        "1950": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 7.166666666666667
                        },
                        "2000": {"speed [m/s]": 4.4, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.333333333333333}
                    }
                }, {
                    "name": "HKG2",
                    "lane": 2,
                    "rank": 4,
                    "athletes": [{
                        "id": 4861,
                        "first_name": "Ho Yin",
                        "last_name": "WONG",
                        "full_name": "WONG, Ho Yin",
                        "boat_position": "b"
                    }, {
                        "id": 4862,
                        "first_name": "Chak Lung",
                        "last_name": "HO",
                        "full_name": "HO, Chak Lung",
                        "boat_position": "s"
                    }],
                    "intermediates": {
                        "500": {
                            "rank": 4,
                            "time [millis]": 122000,
                            "pace [millis]": 122000,
                            "speed [m/s]": 4.098360655737705,
                            "deficit [millis]": 10000,
                            "rel_diff_to_avg_speed [%]": -5.227999550701648
                        },
                        "1000": {
                            "rank": 4,
                            "time [millis]": 247000,
                            "pace [millis]": 125000,
                            "speed [m/s]": 4.0,
                            "deficit [millis]": 19000,
                            "rel_diff_to_avg_speed [%]": -3.471247250342461
                        },
                        "1500": {
                            "rank": 4,
                            "time [millis]": 368000,
                            "pace [millis]": 121000,
                            "speed [m/s]": 4.132231404958677,
                            "deficit [millis]": 21000,
                            "rel_diff_to_avg_speed [%]": -0.4184100418410026
                        }
                    },
                    "race_data": {
                        "50": {"speed [m/s]": 4.3, "stroke [1/min]": 41.0, "propulsion [m/stroke]": 6.2926829268292686},
                        "100": {"speed [m/s]": 3.5, "stroke [1/min]": 39.0, "propulsion [m/stroke]": 5.384615384615385},
                        "150": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 38.0,
                            "propulsion [m/stroke]": 6.7894736842105265
                        },
                        "200": {"speed [m/s]": 4.1, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.648648648648648},
                        "250": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "300": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "350": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "400": {"speed [m/s]": 4.1, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.028571428571428},
                        "450": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "500": {"speed [m/s]": 4.1, "stroke [1/min]": 34.0, "propulsion [m/stroke]": 7.235294117647058},
                        "550": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.2727272727272725
                        },
                        "600": {"speed [m/s]": 4.1, "stroke [1/min]": 33.0, "propulsion [m/stroke]": 7.454545454545453},
                        "650": {"speed [m/s]": 4.1, "stroke [1/min]": 34.0, "propulsion [m/stroke]": 7.235294117647058},
                        "700": {"speed [m/s]": 4.1, "stroke [1/min]": 33.0, "propulsion [m/stroke]": 7.454545454545453},
                        "750": {"speed [m/s]": 3.8, "stroke [1/min]": 33.0, "propulsion [m/stroke]": 6.909090909090909},
                        "800": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.2727272727272725
                        },
                        "850": {"speed [m/s]": 4.0, "stroke [1/min]": 32.0, "propulsion [m/stroke]": 7.5},
                        "900": {"speed [m/s]": 3.9, "stroke [1/min]": 33.0, "propulsion [m/stroke]": 7.090909090909091},
                        "950": {"speed [m/s]": 3.9, "stroke [1/min]": 32.0, "propulsion [m/stroke]": 7.3125},
                        "1000": {"speed [m/s]": 3.9, "stroke [1/min]": 32.0, "propulsion [m/stroke]": 7.3125},
                        "1050": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.454545454545453
                        },
                        "1100": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 32.0,
                            "propulsion [m/stroke]": 7.687499999999999
                        },
                        "1150": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 32.0,
                            "propulsion [m/stroke]": 7.687499999999999
                        },
                        "1200": {"speed [m/s]": 3.9, "stroke [1/min]": 32.0, "propulsion [m/stroke]": 7.3125},
                        "1250": {"speed [m/s]": 4.0, "stroke [1/min]": 32.0, "propulsion [m/stroke]": 7.5},
                        "1300": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.454545454545453
                        },
                        "1350": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.818181818181818
                        },
                        "1400": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.818181818181818
                        },
                        "1450": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.454545454545453
                        },
                        "1500": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.818181818181818
                        },
                        "1550": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 33.0,
                            "propulsion [m/stroke]": 7.818181818181818
                        },
                        "1600": {
                            "speed [m/s]": 4.4,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.542857142857143
                        },
                        "1650": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1700": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1750": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1800": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1850": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.411764705882353
                        },
                        "1900": {
                            "speed [m/s]": 4.4,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.542857142857143
                        },
                        "1950": {
                            "speed [m/s]": 4.4,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.542857142857143
                        },
                        "2000": {"speed [m/s]": 4.4, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.542857142857143}
                    }
                }, {
                    "name": "HKG1",
                    "lane": 4,
                    "rank": 3,
                    "athletes": [{
                        "id": 4863,
                        "first_name": "Yuk Man",
                        "last_name": "CHAN",
                        "full_name": "CHAN, Yuk Man",
                        "boat_position": "b"
                    }, {
                        "id": 4864,
                        "first_name": "Yee Ping",
                        "last_name": "CHAU",
                        "full_name": "CHAU, Yee Ping",
                        "boat_position": "s"
                    }],
                    "intermediates": {
                        "500": {
                            "rank": 3,
                            "time [millis]": 116000,
                            "pace [millis]": 116000,
                            "speed [m/s]": 4.310344827586207,
                            "deficit [millis]": 4000,
                            "rel_diff_to_avg_speed [%]": -0.3259995274620617
                        },
                        "1000": {
                            "rank": 3,
                            "time [millis]": 238000,
                            "pace [millis]": 122000,
                            "speed [m/s]": 4.098360655737705,
                            "deficit [millis]": 10000,
                            "rel_diff_to_avg_speed [%]": -1.0975893958426932
                        },
                        "1500": {
                            "rank": 3,
                            "time [millis]": 359000,
                            "pace [millis]": 121000,
                            "speed [m/s]": 4.132231404958677,
                            "deficit [millis]": 12000,
                            "rel_diff_to_avg_speed [%]": -0.4184100418410026
                        }
                    },
                    "race_data": {
                        "50": {"speed [m/s]": 4.8, "stroke [1/min]": 44.0, "propulsion [m/stroke]": 6.545454545454546},
                        "100": {"speed [m/s]": 4.6, "stroke [1/min]": 42.0, "propulsion [m/stroke]": 6.571428571428571},
                        "150": {"speed [m/s]": 4.4, "stroke [1/min]": 39.0, "propulsion [m/stroke]": 6.769230769230769},
                        "200": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "250": {"speed [m/s]": 4.4, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 7.135135135135135},
                        "300": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "350": {"speed [m/s]": 4.4, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.333333333333333},
                        "400": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "450": {"speed [m/s]": 4.3, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.166666666666667},
                        "500": {"speed [m/s]": 4.3, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.371428571428571},
                        "550": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "600": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "650": {"speed [m/s]": 4.3, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.371428571428571},
                        "700": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "750": {"speed [m/s]": 4.1, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.028571428571428},
                        "800": {"speed [m/s]": 3.9, "stroke [1/min]": 34.0, "propulsion [m/stroke]": 6.882352941176471},
                        "850": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.0588235294117645
                        },
                        "900": {"speed [m/s]": 4.1, "stroke [1/min]": 34.0, "propulsion [m/stroke]": 7.235294117647058},
                        "950": {"speed [m/s]": 4.1, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.028571428571428},
                        "1000": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.0588235294117645
                        },
                        "1050": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.235294117647058
                        },
                        "1100": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1150": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1200": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 6.857142857142857
                        },
                        "1250": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1300": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 6.857142857142857
                        },
                        "1350": {
                            "speed [m/s]": 4.0,
                            "stroke [1/min]": 34.0,
                            "propulsion [m/stroke]": 7.0588235294117645
                        },
                        "1400": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.371428571428571
                        },
                        "1450": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.028571428571428
                        },
                        "1500": {"speed [m/s]": 4.2, "stroke [1/min]": 35.0, "propulsion [m/stroke]": 7.2},
                        "1550": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1600": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1650": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1700": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.8108108108108105
                        },
                        "1750": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 6.833333333333332
                        },
                        "1800": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.8108108108108105
                        },
                        "1850": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.972972972972973
                        },
                        "1900": {
                            "speed [m/s]": 4.5,
                            "stroke [1/min]": 38.0,
                            "propulsion [m/stroke]": 7.105263157894737
                        },
                        "1950": {
                            "speed [m/s]": 4.4,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 7.135135135135135
                        },
                        "2000": {"speed [m/s]": 4.5, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.5}
                    }
                }, {
                    "name": "POR",
                    "lane": 3,
                    "rank": 2,
                    "athletes": [{
                        "id": 4568,
                        "first_name": "Simao",
                        "last_name": "SIMOES",
                        "full_name": "SIMOES, Simao",
                        "boat_position": "s"
                    }, {
                        "id": 4569,
                        "first_name": "Tomas",
                        "last_name": "BARRETO",
                        "full_name": "BARRETO, Tomas",
                        "boat_position": "b"
                    }],
                    "intermediates": {
                        "500": {
                            "rank": 2,
                            "time [millis]": 113000,
                            "pace [millis]": 113000,
                            "speed [m/s]": 4.424778761061947,
                            "deficit [millis]": 1000,
                            "rel_diff_to_avg_speed [%]": 2.3202128744637096
                        },
                        "1000": {
                            "rank": 2,
                            "time [millis]": 233000,
                            "pace [millis]": 120000,
                            "speed [m/s]": 4.166666666666667,
                            "deficit [millis]": 5000,
                            "rel_diff_to_avg_speed [%]": 0.5507841142266106
                        },
                        "1500": {
                            "rank": 2,
                            "time [millis]": 354000,
                            "pace [millis]": 121000,
                            "speed [m/s]": 4.132231404958677,
                            "deficit [millis]": 7000,
                            "rel_diff_to_avg_speed [%]": -0.4184100418410026
                        }
                    },
                    "race_data": {
                        "50": {"speed [m/s]": 4.8, "stroke [1/min]": 49.0, "propulsion [m/stroke]": 5.877551020408164},
                        "100": {"speed [m/s]": 4.7, "stroke [1/min]": 46.0, "propulsion [m/stroke]": 6.130434782608695},
                        "150": {"speed [m/s]": 4.7, "stroke [1/min]": 43.0, "propulsion [m/stroke]": 6.558139534883721},
                        "200": {
                            "speed [m/s]": 4.6,
                            "stroke [1/min]": 43.0,
                            "propulsion [m/stroke]": 6.4186046511627906
                        },
                        "250": {"speed [m/s]": 4.5, "stroke [1/min]": 41.0, "propulsion [m/stroke]": 6.585365853658536},
                        "300": {"speed [m/s]": 4.5, "stroke [1/min]": 40.0, "propulsion [m/stroke]": 6.75},
                        "350": {"speed [m/s]": 4.5, "stroke [1/min]": 40.0, "propulsion [m/stroke]": 6.75},
                        "400": {"speed [m/s]": 4.3, "stroke [1/min]": 39.0, "propulsion [m/stroke]": 6.615384615384615},
                        "450": {"speed [m/s]": 4.3, "stroke [1/min]": 39.0, "propulsion [m/stroke]": 6.615384615384615},
                        "500": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "550": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.8108108108108105
                        },
                        "600": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "650": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "700": {"speed [m/s]": 4.3, "stroke [1/min]": 37.0, "propulsion [m/stroke]": 6.972972972972973},
                        "750": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "800": {"speed [m/s]": 4.1, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 6.833333333333332},
                        "850": {"speed [m/s]": 4.0, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 6.666666666666667},
                        "900": {"speed [m/s]": 4.0, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 6.666666666666667},
                        "950": {"speed [m/s]": 4.1, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 6.833333333333332},
                        "1000": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 6.833333333333332
                        },
                        "1050": {"speed [m/s]": 3.9, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 6.5},
                        "1100": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.028571428571428
                        },
                        "1150": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1200": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 6.833333333333332
                        },
                        "1250": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 35.0,
                            "propulsion [m/stroke]": 7.028571428571428
                        },
                        "1300": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1350": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 6.833333333333332
                        },
                        "1400": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1450": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 36.0,
                            "propulsion [m/stroke]": 6.833333333333332
                        },
                        "1500": {"speed [m/s]": 4.2, "stroke [1/min]": 36.0, "propulsion [m/stroke]": 7.0},
                        "1550": {
                            "speed [m/s]": 4.3,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.972972972972973
                        },
                        "1600": {
                            "speed [m/s]": 4.1,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.648648648648648
                        },
                        "1650": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 37.0,
                            "propulsion [m/stroke]": 6.8108108108108105
                        },
                        "1700": {
                            "speed [m/s]": 4.2,
                            "stroke [1/min]": 39.0,
                            "propulsion [m/stroke]": 6.461538461538462
                        },
                        "1750": {"speed [m/s]": 4.3, "stroke [1/min]": 40.0, "propulsion [m/stroke]": 6.45},
                        "1800": {"speed [m/s]": 4.3, "stroke [1/min]": 40.0, "propulsion [m/stroke]": 6.45},
                        "1850": {"speed [m/s]": 4.5, "stroke [1/min]": 40.0, "propulsion [m/stroke]": 6.75},
                        "1900": {
                            "speed [m/s]": 4.6,
                            "stroke [1/min]": 41.0,
                            "propulsion [m/stroke]": 6.7317073170731705
                        },
                        "1950": {
                            "speed [m/s]": 4.9,
                            "stroke [1/min]": 43.0,
                            "propulsion [m/stroke]": 6.837209302325581
                        },
                        "2000": {"speed [m/s]": 4.8, "stroke [1/min]": 44.0, "propulsion [m/stroke]": 6.545454545454546}
                    }
                }]
            }],
            analysis: null
        },
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getAnalysisData(state) {
            return state.data.analysis
        },
        getCompetitionData(state) {
            const data = state.data.raceData[0]
            data.worldBestTimeBoatClass = formatMilliseconds(data.worldBestTimeBoatClass);
            data.bestTimeBoatClassCurrentOZ = formatMilliseconds(data.bestTimeBoatClassCurrentOZ);
            return data
        },
        getRaceAnalysisFilterOptions(state) {
            return state.data.filterOptions
        },
        getOldTableData(state) {
            return state.data.raceData[0].data
        },
        getLoadingState(state) {
            return state.loadingState
        },
        getTableData(state) {
            const tableHead = ['Platz', 'Bahn', 'Nation', 'Mannschaft'];
            const intermediateDistances = state.data.raceData[0].race_boats[0].intermediates

            for (const key in intermediateDistances) {
                // ignore first as this is the starting value
                if (key !== '0') {
                    tableHead.push(key + "m", "Position")
                }
            }
            const tableData = [];
            tableData.push(tableHead);

            state.data.raceData[0].race_boats.forEach(dataObj => {
                if (dataObj.intermediates !== '0') {
                    const rowData = [dataObj.rank, dataObj.lane, dataObj.name];
                    const athleteNames = Object.values(dataObj.athletes).map(athlete =>
                        `(${athlete.boat_position}) ${athlete.first_name} ${athlete.last_name}`)
                    rowData.push(athleteNames);

                    const firstArray = [];
                    const secondArray = [];
                    const speedValues = [];
                    const strokeValues = [];
                    const propulsionValues = [];

                    Object.values(dataObj.race_data).forEach(gpsData => {
                        if (dataObj.intermediates !== '0') {
                            speedValues.push(gpsData["speed [m/s]"] + "[m/s]");
                            strokeValues.push(gpsData["stroke [1/min]"] + "[1/min]");
                            propulsionValues.push(gpsData["propulsion [m/stroke]"].toFixed(2) + "[m/Schlag]");

                        }
                    });
                    for (const [index, [key, intermediate]] of Object.entries(dataObj.intermediates).entries()) {
                        if (key !== '0') {
                            firstArray.push(
                                formatMilliseconds(intermediate["time [millis]"]),
                                formatMilliseconds(intermediate["pace [millis]"]),
                                formatMilliseconds(intermediate["deficit [millis]"])
                            )
                            secondArray.push(["(" + intermediate["rank"] + ")", speedValues[index], strokeValues[index], propulsionValues[index]])
                        }
                    }
                    const chunkSize = 3;
                    const tempArray = [];
                    for (let i = 0; i < firstArray.length; i += chunkSize) {
                        tempArray.push(firstArray.slice(i, i + chunkSize));
                    }
                    tempArray.forEach((value, index) => {
                        rowData.push(value)
                        rowData.push(secondArray[index])
                    })
                    tableData.push(rowData);
                }
            })
            state.tableExport = tableData
            return tableData;
        },
        getDeficitInMeters(state) {
            const raceBoats = state.data.raceData[0].race_boats
            // determine winner
            const winnerIdx = raceBoats.findIndex(team => team.rank === 1);
            const winnerData = raceBoats.map(dataObj => dataObj.race_data)[winnerIdx]
            const winnerTeamSpeeds = Object.fromEntries(Object.entries(winnerData).map(
                ([key, val]) => [key, val["speed [m/s]"]]));

            // calculate difference to winner based on speed
            let speedPerTeam = {};
            let countries = []
            for (const i in raceBoats) {
                countries.push(raceBoats[i].name)
                const speedData = raceBoats.map(dataObj => dataObj.race_data)[i];
                let diffSpeedValues = {}

                const interval_list = Object.keys(speedData).map((element, index, arr) => (arr[index + 1] || 0) - element)
                const hashmap = interval_list.reduce((acc, val) => {
                    acc[val] = (acc[val] || 0) + 1
                    return acc
                }, {})
                const interval = Object.keys(hashmap).reduce((a, b) => hashmap[a] > hashmap[b] ? a : b)
                let prevValue = 0
                for (const [key, val] of Object.entries(speedData)) {
                    const speedWinner = winnerTeamSpeeds[key]
                    const speedCurrentTeam = val["speed [m/s]"]
                    let time = speedWinner !== 0 ? interval / speedWinner : 0;
                    if (Number(key) !== 0) {
                        prevValue = diffSpeedValues[key - interval]
                    }
                    diffSpeedValues[key] = prevValue + ((speedWinner * time) - (speedCurrentTeam * time))
                }
                speedPerTeam[i] = diffSpeedValues
            }
            let colorIndex = 0;
            const datasets = []
            Object.entries(speedPerTeam).forEach(([key, value], idx) => {
                const label = countries[idx]
                const backgroundColor = COLORS[colorIndex % 6]
                const borderColor = COLORS[colorIndex % 6]
                const data = Object.values(value)
                datasets.push({label, backgroundColor, borderColor, data})
                colorIndex++
            })
            const allKeys = Object.values(speedPerTeam).map(obj => Object.keys(obj))
            return {
                labels: Array.from(new Set([].concat(...allKeys))),
                datasets
            };
        },
        getGPSChartData(state) {
            const chartDataKeys = ['speed [m/s]', 'stroke [1/min]', 'propulsion [m/stroke]'];
            return chartDataKeys.map(key => {
                const datasets = [];
                let colorIndex = 0;

                state.data.raceData[0].race_boats.forEach(dataObj => {
                    const label = dataObj.name;
                    const backgroundColor = COLORS[colorIndex % 6];
                    const borderColor = COLORS[colorIndex % 6];
                    dataObj.race_data["0"] = {'speed [m/s]': 0, 'stroke [1/min]': 0, 'propulsion [m/stroke]': 0}
                    const data = Object.values(dataObj.race_data).map(obj => obj[key]);
                    datasets.push({label, backgroundColor, borderColor, data});
                    colorIndex++;
                });
                return {
                    labels: Object.keys(state.data.raceData[0].race_boats[0].race_data),
                    datasets
                };
            })
        },
        getIntermediateChartData(state) {
            const intermediateDataKeys = ["rank", "deficit [millis]"];
            return intermediateDataKeys.map(key => {
                const datasets = [];
                let colorIndex = 0;
                state.data.raceData[0].race_boats.forEach(dataObj => {
                    const label = dataObj.name;
                    const backgroundColor = COLORS[colorIndex % 6];
                    const borderColor = COLORS[colorIndex % 6];
                    // add zero values as start point
                    dataObj.intermediates["0"] = {"rank": 1, "deficit [millis]": 0}
                    let data = Object.values(dataObj.intermediates).map(distanceObj => distanceObj[key]);
                    if (key === "deficit [millis]") {
                        data = data.map(x => formatMilliseconds(x))
                    }
                    datasets.push({label, backgroundColor, borderColor, data});
                    colorIndex++;
                });
                const chartLabels = Object.keys(state.data.raceData[0].race_boats[0].intermediates)
                return {
                    labels: chartLabels,
                    datasets
                };
            })
        },
        getIntermediateChartOptions(state) {
            const max_val = Math.max(...state.data.raceData[0].race_boats.map(obj =>
                Math.max(...Object.values(obj.intermediates).map(el => el["deficit [millis]"]))
            ));

            return [{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Strecke [m]'
                        }
                    },
                    y: {
                        reverse: true,
                        title: {
                            display: true,
                            text: 'Platzierung'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Platzierung"
                    }
                }
            },
                {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            title: {
                display: true,
                text: 'Strecke [m]'
            }
        },
        y: {
            type: 'time',
            time: {
                parser: 'mm:ss.SS',
                unit: 'millisecond',
                displayFormats: {
                    millisecond: 'mm:ss.SS',
                    tooltip: 'mm:ss.SS'
                }
            },
            min: '00:00.00',
            max: formatMilliseconds(max_val + 100),
            title: {
                display: true,
                text: 'Rückstand [mm:ss.ms]'
            }
        }
    },
    plugins: {
        title: {
            display: true,
            text: "Rückstand zum Führenden [sek]"
        }
    }
}

            ]
        }
    },
    actions: {
        async getFilterOptions() {
            try {
                this.data.filterOptions[0].competition_category_ids = await axios.get(
                    `${import.meta.env.VITE_BACKEND_API_BASE_URL}/competition_category/`
                )
            } catch (error) {
                console.error(error)
            }
        },
        async postFormData(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/competition`, {data})
                .then(response => {
                    this.data.analysis = response.data
                    this.loadingState = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async fetchRaceData(raceId) {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_race/${raceId}/`)
                .then(response => {
                    this.data.raceData[0] = response.data
                    this.loadingState = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        setToLoadingState() {
            this.loadingState = true
        },
        exportTableData() {
            let finalData = []
            for (const data of Object.values(this.tableExport)) {
                let rowData = []
                for (const [, value] of data.entries()) {
                    Array.isArray(value) ? rowData.push(value.join(" | ")) : rowData.push(value)
                }
                finalData.push(rowData)
            }
            const csvContent = "data:text/csv;charset=utf-8," + finalData.map(e => e.join(",")).join("\n");
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "rennstruktur.csv");
            document.body.appendChild(link);
            link.click();
        }
    }
});
import axios from "axios";
import {defineStore} from "pinia";

const formatMilliseconds = ms => {
    if (!ms) {
        return '00:00.00';
    }
    return new Date(ms).toISOString().slice(14, -2);
};

export const useAthletenState = defineStore({
    id: "athleten",
    state: () => ({
        filterOpen: false,
        tableExport: [],
        filterOptions: [{
            "birth_years": [{"start_year": 1950}, {"end_year": 2025}],
            "boat_classes": {
                'm': {
                    'junior': {
                        'single': {"JM1x": "Junior Men's Single Sculls"},
                        'double': {"JM2x": "Junior Men's Double Sculls"},
                        'quad': {"JM4x": "Junior Men's Quadruple Sculls"},
                        'pair': {"JM2-": "Junior Men's Pair"},
                        'coxed_four': {"JM4+": "Junior Men's Coxed Four"},
                        'four': {"JM4-": "Junior Men's Four"},
                        'eight': {"JM8-": "Junior Men's Eight"}
                    },
                    'u19': {},
                    'u23': {
                        'single': {"BM1x": "U23 Men's Single Sculls"},
                        'double': {"BM2x": "U23 Men's Double Sculls"},
                        'quad': {"BM4x": "U23 Men's Quadruple Sculls"},
                        'pair': {"BM2-": "U23 Men's Pair"},
                        'coxed_four': {"BM4+": "U23 Men's Coxed Four"},
                        'four': {"BM4-": "U23 Men's Four"},
                        'eight': {"BM8+": "U23 Men's Eight"},
                        'lw_single': {"BLM1x": "U23 Lightweight Men's Single Sculls"},
                        'lw_double': {"BLM2x": "U23 Lightweight Men's Double Sculls"},
                        'lw_quad': {"BLM4x": "U23 Lightweight Men's Quadruple Sculls"},
                        'lw_pair': {"BLM2-": "U23 Lightweight Men's Pair"},
                    },
                    'elite': {
                        'single': {"M1x": "Men's Single Sculls"},
                        'double': {"M2x": "Men's Double Sculls"},
                        'quad': {"M4x": "Men's Quadruple Sculls"},
                        'pair': {"M2-": "Men's Pair"},
                        'four': {"M4-": "Men's Four"},
                        'eight': {"M8+": "Men's Eight"},
                        'lw_single': {"LM1x": "Lightweight Men's Single Sculls"},
                        'lw_double': {"LM2x": "Lightweight Men's Double Sculls"},
                        'lw_quad': {"LM4x": "Lightweight Men's Quadruple Sculls"},
                        'lw_pair': {"LM2-": "Lightweight Men's Pair"},
                    },
                    'para': {
                        '1': {"PR1 M1x": "PR1 Men's Single Sculls"},
                        '2': {"PR2 M1x": "PR2 Men's Single Sculls"},
                        '3': {"PR3 M2-": "PR3 Men's Pair"}
                    }
                },
                'w': {
                    'junior': {
                        'single': {"JW1x": "Junior Women's Single Sculls"},
                        'double': {"JW2x": "Junior Women's Double Sculls"},
                        'quad': {"JW4x": "Junior Women's Quadruple Sculls"},
                        'pair': {"JW2-": "Junior Women's Pair"},
                        'coxed_four': {"JW4+": "Junior Women's Coxed Four"},
                        'four': {"JW4-": "Junior Women's Four"},
                        'eight': {"JW8-": "Junior Women's Eight"}
                    },
                    'u19': {},
                    'u23': {
                        'single': {"BW1x": "U23 Women's Single Sculls"},
                        'double': {"BW2x": "U23 Women's Double Sculls"},
                        'quad': {"BW4x": "U23 Women's Quadruple Sculls"},
                        'pair': {"BW2-": "U23 Women's Pair"},
                        'coxed_four': {"BW4+": "U23 Women's Coxed Four"},
                        'four': {"BW4-": "U23 Women's Four"},
                        'eight': {"BW8+": "U23 Women's Eight"},
                        'lw_single': {"BLW1x": "U23 Lightweight Women's Single Sculls"},
                        'lw_double': {"BLW2x": "U23 Lightweight Women's Double Sculls"},
                        'lw_quad': {"BLW4x": "U23 Lightweight Women's Quadruple Sculls"},
                        'lw_pair': {"BLW2-": "U23 Lightweight Women's Pair"},
                    },
                    'elite': {
                        'single': {"W1x": "Women's Single Sculls"},
                        'double': {"W2x": "Women's Double Sculls"},
                        'quad': {"W4x": "Women's Quadruple Sculls"},
                        'pair': {"W2-": "Women's Pair"},
                        'four': {"W4-": "Women's Four"},
                        'eight': {"W8+": "Women's Eight"},
                        'lw_single': {"LW1x": "Lightweight Women's Single Sculls"},
                        'lw_double': {"LW2x": "Lightweight Women's Double Sculls"},
                        'lw_quad': {"LW4x": "Lightweight Women's Quadruple Sculls"},
                        'lw_pair': {"LW2-": "Lightweight Women's Pair"},
                    },
                    'para': {
                        '1': {"PR1 W1x": "PR1 Women's Single Sculls"},
                        '2': {"PR2 W1x": "PR2 Women's Single Sculls"},
                        '3': {"PR3 W2-": "PR3 Women's Pair"}
                    }
                },
                'mixed': {
                    'double_2': {"PR2 Mix2x": "PR2 Mixed Double Sculls"},
                    'double_3': {"PR3 Mix2x": "PR3 Mixed Double Sculls"},
                    'four': {"PR3 Mix4+": "PR3 Mixed Coxed Four"},
                },
                'all': {
                    'all': {"Alle Bootsklassen": "Alle"}
                },
            },
            "nations": {}
        }],
        data: {
            "id": null,
            "name": null,
            "dob": null,
            "gender": null,
            "nation": null,
            "weight": 0,
            "height": 0,
            "disciplines": [],
            "boat_class": "",
            "num_of_races": 0,
            "medals_total": 0,
            "medals_gold": 0,
            "medals_silver": 0,
            "medals_bronze": 0,
            "final_a": 0,
            "final_b": 0,
            "best_time_boat_class": 0,
            "best_time_current_oz": 0,
            "race_list": [{
                "race_id": null,
                "name": null,
                "boat_class": null,
                "rank": null,
                "start_time": null,
                "venue": null,
            }]
        },
        previewAthleteResults: []
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getPreviewAthleteResults(state) {
            return state.previewAthleteResults
        },
        getAthletenFilterOptions(state) {
            return state.filterOptions
        },
        getTableData(state) {
            const athleteData = state.data.athlete

            if (athleteData && athleteData.race_list) {
                const athleteValues = Object.entries(athleteData).map(([key, val]) => {
                    if (typeof val === 'string') {
                        return val.replace(/,/g, ' ');
                    } else if (val !== null) {
                        return val;
                    } else {
                        return null
                    }
                }).filter(val => val !== null);
                state.tableExportAthlete = [Object.keys(athleteData).filter((v) => v !== "race_list"), athleteValues];

                let raceListExportData = [Object.keys(athleteData.race_list[0])];
                Object.values(athleteData.race_list).forEach(race => {
                    race["result_time"] = formatMilliseconds(race["result_time"])
                    const subArray = Object.values(race).map(el => String(el).replace(/,/g, ' '));
                    raceListExportData = raceListExportData.concat([subArray]);
                })
                state.tableExportAthleteRaceList = raceListExportData;
            }
            return athleteData
        }
    },
    actions: {
        async fetchAthletesFilterOptions() {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_athletes_filter_options`)
                .then(response => {
                    this.filterOptions = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postSearchAthlete(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_athlete_by_name/`, {data})
                .then(response => {
                    this.previewAthleteResults = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async getAthlete(data) {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_athlete/${data.id}`)
                .then(response => {
                    this.data.athlete = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        exportTableData() {
            var weight = 0;
            var height = 0;
            var gender = "";

            if(this.data.athlete.weight > 0) {
                weight = this.data.athlete.weight + "kg"
            } else {
                weight = "-"
            }

            if(this.data.athlete.height > 0) {
                height = this.data.athlete.height + "cm"
            } else {
                height = "-"
            }

            if(this.data.athlete.gender == "Men") {
                gender = "Männlich"
            } else {
                gender = "Weiblich"
            }

            var disciplines = []
            for(const item of this.data.athlete.disciplines) {
                disciplines.push(item)
            }
            disciplines = disciplines.toString()

            const csvContent = "data:text/csv;charset=utf-8,"
                + "Name,Nation,Geburtsdatum,Geschlecht,Gewicht,Größe,Bootsklasse(n),Disziplin(en),Rennanzahl,Medaillen Gesamt,Medaillen Gold,Medaillen Silber,Medaillen Bronze,Finale A,Finale B\n"
                + this.data.athlete.name.replaceAll(",", " ") + ","
                + this.data.athlete.nation + ","
                + this.data.athlete.dob + ","
                + gender + ","
                + weight + ","
                + height + ","
                + this.data.athlete.boat_class.replaceAll(",", " |") + ","
                + disciplines.replaceAll(",", " | ") + ","
                + this.data.athlete.num_of_races + ","
                + this.data.athlete.medals_total + ","
                + this.data.athlete.medals_gold + ","
                + this.data.athlete.medals_silver + ","
                + this.data.athlete.medals_bronze + ","
                + this.data.athlete.final_a + ","
                + this.data.athlete.final_b
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `${this.data.athlete.name.replace(", ", "_")}_Profile.csv`);
            document.body.appendChild(link);
            link.click();

            const csvContentRaceList = "data:text/csv;charset=utf-8," + this.tableExportAthleteRaceList.map(row => row.join(",")).join("\n");
            const encodedUriRaceList = encodeURI(csvContentRaceList);
            const linkRaceList = document.createElement("a");
            linkRaceList.setAttribute("href", encodedUriRaceList);
            linkRaceList.setAttribute("download", `${this.data.athlete.name.replace(", ", "_")}_Races.csv`);
            document.body.appendChild(linkRaceList);
            linkRaceList.click();
        }
    }
})

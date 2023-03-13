import axios from "axios";
import {defineStore} from "pinia";

// function to convert milliseconds to min:sec:ms
const formatMilliseconds = ms => {
    if (!ms) {
        return '00:00.00';
    }

    const is_string = typeof ms === 'string' || ms instanceof String;
    if (is_string) {
        return ms;
    }

    return new Date(ms).toISOString().slice(14, -2);
};

function roundToTwoDecimal(num) {
    return num ? Number(num.toFixed(2)) : num;
}


// predefined colors for charts
const COLORS = ['#0C67F7', '#93E9ED', '#E0A9FA', '#E0B696', '#E0FAAC', '#F0E95A'];

export const useRennstrukturAnalyseState = defineStore({
    id: "base",
    state: () => ({
        filterOpen: false,
        loadingState: false,
        compData: [],
        tableExport: [],
        outlierCountries: new Set(),
        data: {
            filterOptions: {
                "years": [0, 0],
                "competition_categories": []
            },
            raceData: [{
                "race_id": "",
                "display_name": "",
                "start_date": "",
                "venue": "",
                "boat_class": "",
                "result_time_world_best": 0,
                "result_time_best_of_current_olympia_cycle": 0,
                "progression_code": "",
                "pdf_urls": {
                    "result": "",
                    "race_data": ""
                },
                "race_boats": [{
                    "name": "",
                    "lane": 1,
                    "rank": 1,
                    "athletes": [{
                        "first_name": "",
                        "last_name": "",
                        "boat_position": ""
                    }],
                    "intermediates": {},
                    "race_data": {}
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
            data.worldBestTimeBoatClass = formatMilliseconds(data.result_time_world_best);
            data.bestTimeBoatClassCurrentOZ = formatMilliseconds(data.result_time_best_of_current_olympia_cycle);
            state.compData = data
            return data
        },
        getRaceAnalysisFilterOptions(state) {
            return state.data.filterOptions
        },
        getOutlierCountries(state) {
            return state.outlierCountries
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

            state.data.raceData[0].race_boats.forEach((dataObj, countryIdx) => {
                if (dataObj.intermediates !== '0') {
                    const rowData = [dataObj.rank, dataObj.lane, dataObj.name];
                    const athleteNames = Object.values(dataObj.athletes).map(athlete => {
                        const link = `/athleten?athlete_id=${athlete.id}`;
                        const name = `(${athlete.boat_position}) ${athlete.first_name} ${athlete.last_name}`;
                        return {link, name};
                    });
                    rowData.push(athleteNames);

                    const firstArray = [];
                    const secondArray = [];
                    const propulsionValues = [];

                    Object.values(dataObj.race_data).forEach(gpsData => {
                        if (dataObj.intermediates !== '0') {
                            const propVal = gpsData["propulsion [m/stroke]"]
                            propulsionValues.push(propVal ? roundToTwoDecimal(propVal) : 0);
                        }
                    });
                    for (const [index, [key, intermediate]] of Object.entries(dataObj.intermediates).entries()) {
                        if (key !== '0') {
                            if (intermediate["is_outlier"]) {
                                state.outlierCountries.add(countryIdx)
                            }
                            firstArray.push(
                                formatMilliseconds(intermediate["time [millis]"]),
                                formatMilliseconds(intermediate["pace [millis]"]),
                                formatMilliseconds(intermediate["deficit [millis]"])
                            )

                            const strokeVal = intermediate["stroke [1/min]"]
                            const speedVal = intermediate["speed [m/s]"]
                            const propulsionVal = propulsionValues[index]
                            secondArray.push([
                                "(" + intermediate["rank"] + ")",
                                speedVal ? roundToTwoDecimal(speedVal) + "[m/s]" : "–",
                                strokeVal ? roundToTwoDecimal(strokeVal) + "[1/smin]" : "–",
                                propulsionVal ? roundToTwoDecimal(propulsionVal) + "[m/Schlag]" : "–"
                            ])
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
            // changes for correct representation in csv export
            // deep copy here so the changes for the export won't change the original table data
            let tableExportData = JSON.parse(JSON.stringify(tableData));
            for (let i = 1; i < tableExportData.length; i++) {
                tableExportData[i][3] = tableExportData[i][3].map(el => el.name);
            }
            state.tableExport = tableExportData;

            // return original table data for rendering
            return tableData;
        },
        getDeficitInMeters(state) {
            const raceBoats = state.data.raceData[0].race_boats;
            // determine winner
            const winnerIdx = raceBoats.findIndex(team => team.rank === 1);
            const winnerData = raceBoats.map(dataObj => dataObj.race_data)[winnerIdx];
            const winnerTeamSpeeds = Object.fromEntries(Object.entries(winnerData).map(
                ([key, val]) => [key, val["speed [m/s]"]]
            ));
            // calculate difference to winner based on speed
            let speedPerTeam = {};
            let countries = [];
            for (let i = 0; i < raceBoats.length; i++) {
                countries.push(raceBoats[i].name);
                const speedData = raceBoats[i].race_data;
                let diffSpeedValues = {};

                const intervals = Object.keys(speedData).map((key, index, keys) => {
                    if (index === keys.length - 1) return 0;
                    return keys[index + 1] - key;
                }).filter(interval => interval !== 0);

                const counts = {};
                intervals.forEach(interval => counts[interval] = (counts[interval] || 0) + 1);

                const interval = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b, 0);

                if (interval !== 0) {
                    let prevValue = 0;
                    for (const [key, val] of Object.entries(speedData)) {
                        const speedWinner = winnerTeamSpeeds[key];
                        const speedCurrentTeam = val["speed [m/s]"];
                        let time = speedWinner !== 0 ? interval / speedWinner : 0;
                        if (Number(key) !== 0) {
                            prevValue = diffSpeedValues[key - interval] || 0;
                        }
                        diffSpeedValues[key] = prevValue + ((speedWinner * time) - (speedCurrentTeam * time));
                    }
                    speedPerTeam[i] = diffSpeedValues;
                }
            }
            let colorIndex = 0
            const datasets = []
            Object.entries(speedPerTeam).forEach(([key, value], idx) => {
                const label = countries[idx]
                const backgroundColor = COLORS[colorIndex % 6]
                const borderColor = COLORS[colorIndex % 6]
                const data = Object.values(value)
                datasets.push({label, backgroundColor, borderColor, data})
                colorIndex++;
            });
            const allKeys = Object.values(speedPerTeam).map(obj => Object.keys(obj))
            return {
                labels: Array.from(new Set([].concat(...allKeys))),
                datasets,
            };
        },
        getGPSChartData(state) {
            const chartDataKeys = ['speed [m/s]', 'stroke [1/min]', 'propulsion [m/stroke]']
            return chartDataKeys.map(key => {
                const datasets = []
                let colorIndex = 0

                state.data.raceData[0].race_boats.forEach(dataObj => {
                    const label = dataObj.name
                    const backgroundColor = COLORS[colorIndex % 6]
                    const borderColor = COLORS[colorIndex % 6]
                    //dataObj.race_data["0"] = {'speed [m/s]': 0, 'stroke [1/min]': 0, 'propulsion [m/stroke]': 0}
                    const data = Object.values(dataObj.race_data).map(obj => obj[key])
                    datasets.push({label, backgroundColor, borderColor, data})
                    colorIndex++
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
                                unit: 'second',
                                displayFormats: {
                                    second: 'mm:ss.SS',
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
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/race_analysis_filter_options/`)
                .then(response => {
                    this.data.filterOptions = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postFormData(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/race_analysis_filter_results`, {data})
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
        async fetchCompetitionData(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/race_analysis_filter_results`, {data})
                .then(response => {
                    this.data.analysis = response.data
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
            var progression = null
            if (this.compData.progression_code) {
                progression = this.compData.progression_code
            } else {
                progression = "-"
            }

            for (const data of Object.values(this.tableExport)) {
                let rowData = []
                for (const [, value] of data.entries()) {
                    Array.isArray(value) ? rowData.push(value.join(" | ")) : rowData.push(value)
                }
                finalData.push(rowData)
            }
            const csvContent = "data:text/csv;charset=utf-8,"
                + "Rennen," + this.compData.display_name + "\n"
                + "Ort," + this.compData.venue.replace(",", " |") + "\n"
                + "Startzeit," + this.compData.start_date + "\n"
                + "Weltbestzeit," + this.compData.worldBestTimeBoatClass + "\n"
                + "Bestzeit laufender OZ/Jahr," + this.compData.bestTimeBoatClassCurrentOZ + "\n"
                + "Progression," + progression
                + "\n\n"
                + finalData.map(e => e.join(",")).join("\n")
            ;
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Rennstruktur_" + this.compData.boat_class + ".csv");
            document.body.appendChild(link);
            link.click();
        }
    }
});
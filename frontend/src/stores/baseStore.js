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
            multiple: null,
            analysis: null
        },
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getMultiple(state) {
            return state.data.multiple
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
        getMultipleTableData(state) {
            const tableData = []
            const tableHead = [
                {text: 'Gruppe', tooltip: "Gruppe (Anzahl Rennen)"},
                {text: 'Zeitraum', tooltip: null},
                {text: 'Events', tooltip: null},
                {text: 'Läufe', tooltip: "Läufe (Platzierungen)"},
                {text: 'Nation', tooltip: null},
                {text: 'Zeit', tooltip: "mm:ss"},
                {text: '500m', tooltip: "Zeit (Platzierung), Pace (rel. Pace), Schläge pro Minute (m/s)"},
                {text: '1000m', tooltip: "Zeit (Platzierung), Pace (rel. Pace), Schläge pro Minute (m/s)"},
                {text: '1500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge pro Minute (m/s)"},
                {text: '2000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge pro Minute (m/s)"},
                {text: 'Relationszeit', tooltip: "zu aktueller Bestzeit"},
                {text: 'Rennstruktur', tooltip: null}
            ]
            tableData.push(tableHead)
            
            for (const group of state.data.multiple.groups) {
                const time_period = `${group.min_year} - ${group.max_year}`
                const name = `${group.name} (${group.count})`
                let totalTime = 0
                if (group.stats[2000] && group.stats[2000]["time [millis]"]) {
                    totalTime =  group.stats[2000]["time [millis]"]["mean"]
                }
                //dispalys time, rank, pace, relative pace, strokeFrequency and propulsion for each 500m section
                const intermediate_values = [];

                for (const [index, [key, intermediate]] of Object.entries(group.stats).entries()) {
                    if (key !== '0') {
                        if (intermediate["is_outlier"]) {
                            state.outlierCountries.add(countryIdx)
                        }
                        if(totalTime != 'DNS' && totalTime != 0) {
                            const time = intermediate["time [millis]"]["mean"]
                            const rank = intermediate["rank"]["mean"]
                            const pace = intermediate["pace [millis]"]["mean"]
                            const relativePace = (pace / totalTime * 400).toFixed(1)
                            const strokeFrequency = intermediate["stroke [1/min]"] ? roundToTwoDecimal(intermediate["stroke [1/min]"]).toString() : "-"
                            const speed = intermediate["speed [m/s]"]["mean"] ? roundToTwoDecimal(intermediate["speed [m/s]"]["mean"]): "-"
                       
                            intermediate_values.push([
                                `${formatMilliseconds(time)} (${rank.toFixed(1)})`,
                                `${formatMilliseconds(pace)} (${relativePace}%)`,
                                `${strokeFrequency} spm (${speed} m/s)`]
                            )
                        }
                        else {
                            intermediate_values.push('-')
                        }
                    }
                }

                const rowData = [name, time_period, group.events, group.phases, group.country, formatMilliseconds(totalTime)]

                //500m, 1000m, 1500m, 2000m
                intermediate_values.forEach(value => {
                    rowData.push(value)
                })

                //Relationszeit
                let relationsZeit = "-"
                if (totalTime != 0) {
                    relationsZeit = (state.data.multiple.world_best_time / totalTime * 100).toFixed(1)
                    rowData.push(`${relationsZeit}%`)
                    rowData.push(group.pacing_profile)  //Rennstruktur
                }
                if (rowData.length < tableHead.length) {
                    rowData.push(...(new Array(tableHead.length - rowData.length).fill("-")))
                }
                

                tableData.push(rowData)
            }
            console.log(state.data.multiple)
            
            
            return tableData
        },
        getTableData(state) {
            /*
            return [["Anzahl", "Zeitraum", "Events", "Position", "Strecken", "Nationen", "Zeit", "500m", "1000m", "1500m", "2000m", "Relationszeit"],
                    ["5", ["2023 -", "2024"], ["WCH", "WCP"], ["1,2,3 (1,8)", "fa, fb, fc"],["Luzern", "Varese"], "Ger, FRA, NED, USA",
                    "6:32.05", "1:56.56 (896)", "1:56.56 (896)","1:56.56 (896)","1:56.56 (896)", "?"]]
                    */
           
            const tableData = [];
            const tableHead = ['Platz', 'Bahn', 'Nation', 'Mannschaft', 'Zeit'];

            console.log(state.data.raceData[0])


            const intermediateDistances = state.data.raceData[0].race_boats[0].intermediates
            for (const key in intermediateDistances) {
                // ignore first as this is the starting value
                if (key !== '0') {
                    tableHead.push(key + "m")
                }
            }
            tableHead.push('Relationszeit')
            tableData.push(tableHead)

            //Iterate over participating race boats
            state.data.raceData[0].race_boats.forEach((dataObj, countryIdx) => {
                if (dataObj.intermediates !== '0') {
                    //Platz, Bahn, Nation
                    const rowData = [dataObj.rank, dataObj.lane, dataObj.name];
                    const athleteNames = Object.values(dataObj.athletes).map(athlete => {
                        const link = `/athleten?athlete_id=${athlete.id}`;
                        const name = `(${athlete.boat_position}) ${athlete.first_name} ${athlete.last_name}`;
                        return {link, name};
                    });
                    //Mannschaft
                    rowData.push(athleteNames);
                    
                    var totalTime = 0
                    if (dataObj.intermediates && dataObj.intermediates[2000] && dataObj.intermediates[2000]["time [millis]"]) {
                        totalTime = dataObj.intermediates[2000]["time [millis]"]
                        if(totalTime == 'NaN') {        //TODO: Mehrere Aunahmen, nicht nur DNS!
                            totalTime = 'DNS'
                        }
                    }
                    //Zeit
                    rowData.push(formatMilliseconds(totalTime))

                    //dispalys time, rank, pace, relative pace, strokeFrequency and propulsion for each 500m section
                    const intermediate_values = [];

                    for (const [index, [key, intermediate]] of Object.entries(dataObj.intermediates).entries()) {
                        if (key !== '0') {
                            if (intermediate["is_outlier"]) {
                                state.outlierCountries.add(countryIdx)
                            }
                            if(totalTime != 'DNS' || totalTime == 0) {
                                const time = intermediate["time [millis]"]
                                const rank = intermediate["rank"]
                                const pace = intermediate["pace [millis]"]
                                const relativePace = (pace / totalTime * 400).toFixed(1)
                                const strokeFrequency = intermediate["stroke [1/min]"] ? roundToTwoDecimal(intermediate["stroke [1/min]"]).toString() : "-"
                                const speed = intermediate["speed [m/s]"] ? roundToTwoDecimal(intermediate["speed [m/s]"]): "-"
                           
                                intermediate_values.push([
                                    `${formatMilliseconds(time)} (${rank})`,
                                    `${formatMilliseconds(pace)} (${relativePace}%)`,
                                    `${strokeFrequency}spm (${speed}m/s)`]
                                )
                            }
                            else {
                                intermediate_values.push('-')
                            }
                        }
                    }
                    
                    //500m, 1000m, 1500m, 2000m
                    intermediate_values.forEach(value => {
                        rowData.push(value)
                    })

                    //Relationszeit
                    const relationsZeit = (state.data.raceData[0].result_time_world_best / totalTime * 100).toFixed(1)
                    rowData.push(`${relationsZeit}%`)
                    
                    tableData.push(rowData);
                }
            })
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
                data.splice(0,0,0)           //add data at position 0
                datasets.push({label, backgroundColor, borderColor, data})
                colorIndex++;
            });
            const allKeys = Object.values(speedPerTeam).map(obj => Object.keys(obj))
            return {
                labels: ['0', ...Array.from(new Set([].concat(...allKeys)))],       //Add 0 in x-axis
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
                    const data = Object.values(dataObj.race_data).map(obj => obj[key])
                    data.splice(0,0,null)           //No value at 0
                    datasets.push({label, backgroundColor, borderColor, data})
                    colorIndex++
                });
                return {
                    labels: ['0', ...Object.keys(state.data.raceData[0].race_boats[0].race_data)], //Add 0 in x-axis
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
            const number_of_boats = state.data.raceData[0].race_boats.length

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
                        },
                        ticks: {
                            stepSize: 1
                        },
                        min: 1,
                        max: number_of_boats
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Platzierung"
                    },
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
                    this.data.multiple = null
                    this.loadingState = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postMultipleFormData(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_race_boat_groups`, {data})
                .then(response => {
                    this.data.multiple = response.data
                    this.data.analysis = null
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
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

function calculatePropulsion(speed, strokeFrequency) {
    if(speed != '-' && strokeFrequency != '-' && strokeFrequency != 0) {
        return  (speed * 60 / strokeFrequency).toFixed(1)
    }
    else {
        return '-'
    }

}

function createCSV(content, title) {
    const csvContent = "data:text/csv;charset=utf-8," + content
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "Rennstruktur_" + title + ".csv");
    document.body.appendChild(link);
    link.click(); 
}

function createChartOptions(boats) {
    const firstBoat = boats.find(boat => boat.rank == 1)
    return {
        boats: boats.map(boat => boat.name),
        difference_to: firstBoat.name,
        boats_in_chart: boats.map(boat => boat.name)
    }
}


function intermediateChartOptions(state, number_of_boats, max_val) {
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
            legend: {
                onClick: (evt, legendItem, legend) => {
                   //Update boats_in_chart
                   const hidden = !legendItem.hidden;
                   state.setChartOptionBoats(hidden, legendItem.text)
                },
               
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
            },
            legend: {
                onClick: (evt, legendItem, legend) => {
                   //Update boats_in_chart
                   const hidden = !legendItem.hidden;
                   state.setChartOptionBoats(hidden, legendItem.text)
                },
               
            },
        }
    }
    ]
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
                "chartOptions": {
                    boats: [],
                    difference_to: "",
                    boats_in_chart: []
                },
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
                {text: 'Zeit', tooltip: "mm:ss; Speed"},
                {text: '500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '1000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '1500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '2000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: 'Relationszeit', tooltip: "zu aktueller Bestzeit"},
                {text: 'Rennstruktur', tooltip: null}
            ]
            tableData.push(tableHead)
            
            for (const group of state.data.multiple.groups) {
                const time_period = `${group.min_year} - ${group.max_year}`
                const name = `${group.name} (${group.count})`
                let totalTime = 0
                let averageSpeed = 0
                if (group.stats[2000] && group.stats[2000]["time [millis]"]) {
                    totalTime =  group.stats[2000]["time [millis]"]["mean"]
                    averageSpeed = 2000 * 1000 / totalTime
                    
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
                            const strokeFrequency = intermediate["stroke [1/min]"] ? intermediate["stroke [1/min]"]["mean"].toFixed(1).toString() : "-"
                            const speed = intermediate["speed [m/s]"]["mean"] ? intermediate["speed [m/s]"]["mean"].toFixed(1): "-"
                            const propulsion = calculatePropulsion(speed, strokeFrequency)
                       
                            intermediate_values.push([
                                `${formatMilliseconds(time)} (${rank.toFixed(1)})`,
                                `${formatMilliseconds(pace)} (${relativePace}%)`,
                                `${strokeFrequency} spm`,
                                `${propulsion} m/Schlag`,
                                `${speed} m/s`
                            ]
                            )
                        }
                        else {
                            intermediate_values.push('-')
                        }
                    }
                }

                const runs = group.phases.concat(` (${group.ranks.join(', ')})`)
                const rowData = [name, time_period, group.events, runs, group.country, [formatMilliseconds(totalTime), `${averageSpeed.toFixed(1)} m/s`]]

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
        getChartOptions(state) {
            return state.data.raceData[0].chartOptions
        },
        getTableData(state) {
            
            const tableData = [];
            const tableHead = [
                {text: 'Platz', tooltip: null},
                {text: 'Bahn', tooltip: null},
                {text: 'Nation', tooltip: null},
                {text: 'Mannschaft', tooltip: null},
                {text: 'Zeit', tooltip: "mm:ss; Speed"},
                {text: '500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '1000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '1500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: '2000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute; Meter/Schlag; Speed"},
                {text: 'Relationszeit', tooltip: "zu aktueller Bestzeit"}
            ]
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
                    var averageSpeed = 0
                    if (dataObj.intermediates && dataObj.intermediates[2000] && dataObj.intermediates[2000]["time [millis]"]) {
                        totalTime = dataObj.intermediates[2000]["time [millis]"]
                        averageSpeed = 2000 * 1000 / totalTime
                        if(totalTime == 'NaN') {        //TODO: Mehrere Aunahmen, nicht nur DNS!
                            totalTime = 'DNS'
                            averageSpeed = '-'
                        }
                    }
                    //Zeit
                    rowData.push([formatMilliseconds(totalTime), `${averageSpeed.toFixed(1)} m/s`])

                    //dispalys time, rank, pace, relative pace, strokeFrequency, propulsion and speed for each 500m section
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
                                const propulsion = calculatePropulsion(speed, strokeFrequency)
                           
                                intermediate_values.push([
                                    `${formatMilliseconds(time)} (${rank})`,
                                    `${formatMilliseconds(pace)} (${relativePace}%)`,
                                    `${strokeFrequency} spm`,
                                    `${propulsion} m/Schlag`,
                                    `${speed} m/s`
                                ]

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
            console.log(state.data.raceData)
            return tableData;
        

        },
        getDeficitInMeters(state) {
            const raceBoats = state.data.raceData[0].race_boats;
            const referenceBoat = state.data.raceData[0].chartOptions.difference_to
            // get reference boat to calculate difference
            const winnerIdx = raceBoats.findIndex(team => team.name === referenceBoat);
            const winnerData = raceBoats.map(dataObj => dataObj.race_data)[winnerIdx];
            const winnerTeamSpeeds = Object.fromEntries(Object.entries(winnerData).map(
                ([key, val]) => [key, val["speed [m/s]"]]
            ));
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
                var hidden = true
                if (state.data.raceData[0].chartOptions.boats_in_chart.includes(label)) {
                     hidden = false
                }
                datasets.push({label, backgroundColor, borderColor, data, hidden})
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
                    var hidden = true
                    if (state.data.raceData[0].chartOptions.boats_in_chart.includes(label)) {
                        hidden = false
                    }

                    data.splice(0,0,null)           //No value at 0
                    datasets.push({label, backgroundColor, borderColor, data, hidden})
                    colorIndex++
                });
                return {
                    labels: ['0', ...Object.keys(state.data.raceData[0].race_boats[0].race_data)], //Add 0 in x-axis
                    datasets
                };
            })
        },
        getMeanGPSChartData(state) {
            const chartDataKeys = ['speed [m/s]', 'stroke [1/min]', 'propulsion [m/stroke]']
            return chartDataKeys.map(key => {
                const datasets = []
                let colorIndex = 0

                state.data.multiple.groups.forEach(dataObj => {
                    const label = dataObj.name
                    const backgroundColor = COLORS[colorIndex % 6]
                    const borderColor = COLORS[colorIndex % 6]
                    const data = Object.values(dataObj.stats_race_data).map(obj => obj[key]["mean"])
                    data.splice(0,0,null)           //No value at 0
                    datasets.push({label, backgroundColor, borderColor, data})
                    colorIndex++
                });
                return {
                    labels: ['0', ...Object.keys(state.data.multiple.groups[0].stats_race_data)], //Add 0 in x-axis
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
                    if (key == "deficit [millis]") {
                        data = data.map(x => formatMilliseconds(x))
                    }
                    var hidden = true
                    if (state.data.raceData[0].chartOptions.boats_in_chart.includes(label)) {
                        hidden = false
                    }
                    datasets.push({label, backgroundColor, borderColor, data, hidden});
                    colorIndex++;
                });
                const chartLabels = Object.keys(state.data.raceData[0].race_boats[0].intermediates)
                return {
                    labels: chartLabels,
                    datasets
                };
            })
        },
        getMeanIntermediateChartData(state) {
            const intermediateDataKeys = ["rank"];
            return intermediateDataKeys.map(key => {
                const datasets = [];
                let colorIndex = 0;
                state.data.multiple.groups.forEach(dataObj => {
                    const label = dataObj.name;
                    const backgroundColor = COLORS[colorIndex % 6];
                    const borderColor = COLORS[colorIndex % 6];
                    let data = Object.values(dataObj.stats).map(distanceObj => distanceObj[key]["mean"]);
                    data.splice(0,0,1)
                    datasets.push({label, backgroundColor, borderColor, data});
                    colorIndex++;
                });
                const chartLabels = [0, ...Object.keys(state.data.multiple.groups[0].stats)]
                return {
                    labels: chartLabels,
                    datasets
                };
            })
        },
        getCountData(state) {
            let datasets = []
            let datas = []
            const labels = []
            let barColors = []
            let colorIndex = 0
            state.data.multiple.groups.forEach(dataObj => {
                const label = dataObj.name;
                const backgroundColor = COLORS[colorIndex % 6];
                const borderColor = COLORS[colorIndex % 6];
                barColors.push(COLORS[colorIndex % 6])
                //let data = dataObj.count
                datas.push(dataObj.count)
                //datasets.push({label, backgroundColor, borderColor, data});
                labels.push(label)
                colorIndex++;
            });
            datasets.push({datas})
            return {
                labels: labels,
                datasets: [{
                    barPercentage: 0.8,
                    barThickness: 18,
                    maxBarThickness: 18,
                    minBarLength: 2,
                    backgroundColor: barColors,
                    borderColor: barColors,

                    data: datas, 
                    label: "Alle Gruppen"
                }]
            };
            
        },
        getMeanIntermediateChartOptions(state) {
            const number_of_boats = state.data.multiple.groups.length
            return intermediateChartOptions(state, 6, 0)

        },
        getIntermediateChartOptions(state) {
            const max_val = Math.max(...state.data.raceData[0].race_boats.map(obj =>
                Math.max(...Object.values(obj.intermediates).map(el => el["deficit [millis]"]))
            ));
            const number_of_boats = state.data.raceData[0].race_boats.length
            return intermediateChartOptions(state, number_of_boats, max_val)
        },
        getPacingProfiles(state) {
            const labels = Object.keys(state.data.multiple.groups[0].stats)
            const datasets = [];
            let colorIndex = 0;
            const dataKeys = ["mean", "lower_bound", "upper_bound"];
            state.data.multiple.groups.forEach(group => {
                const label = group.name;
                dataKeys.forEach(key => {
                    let backgroundColor
                    let borderColor
                    const data = Object.values(group.stats).map(obj => obj["rel_speed [%]"][key])
                    if (key == "mean") {
                        backgroundColor = COLORS[colorIndex % 6];
                        borderColor = COLORS[colorIndex % 6];
                        datasets.push({ label, backgroundColor, borderColor, data });
                    }
                    else {
                        backgroundColor = COLORS[colorIndex % 6].concat("15");
                        borderColor = COLORS[colorIndex % 6].concat("15");
                        const pointRadius = 0
                        //const borderWidth = 0
                        let fill = false
                        if (key == "upper_bound") {
                            fill = "-1"
                        }
                        //const legend = { display: false }
                        datasets.push({ label, backgroundColor, borderColor, data, pointRadius, fill});
                    }
                })

                colorIndex++;

            })
            return {
                labels: labels,
                datasets
            }
        },
        getPacingProfileChartOptions(state) {
            return {
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
                        title: {
                            display: true,
                            text: 'Normalisierte Geschschwindigkeit'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Rennstruktur"
                    },
                    legend: {
                        labels: {
                            filter: function (item, chart) {
                                // Show legend only for 'Dataset 1'
                                return item.datasetIndex  % 3 == 0;
                            }
                        },
                        onClick: (evt, legendItem, legend) => {
                            let newVal = !legendItem.hidden;
                            legend.chart.data.datasets.forEach(dataset => {
                                if (dataset.label === legendItem.text) {
                                    dataset.hidden = newVal
                                }
                            });
                            legend.chart.update();
                        },
                    }
                }
            }
        },
        getDeficitChartOptions(state) {
            return {
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
                        title: {
                            display: true,
                            text: 'Differenz [m]'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Differenz [m]"
                    },
                    legend: {
                        onClick: (evt, legendItem, legend) => {
                           //Update boats_in_chart
                           const hidden = !legendItem.hidden;
                           state.setChartOptionBoats(hidden, legendItem.text)
                        },
                       
                    },
                }
            }
        },
        getGpsChartOptions(state) {
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
                    title: {
                      display: true,
                      text: 'Geschwindigkeit [m/sek]'
                    }
                  }
                },
                plugins: {
                  title: {
                    display: true,
                    text: "Geschwindigkeit"
                  },
                  legend: {
                    onClick: (evt, legendItem, legend) => {
                       //Update boats_in_chart
                       const hidden = !legendItem.hidden;
                       state.setChartOptionBoats(hidden, legendItem.text)
                    },
                   
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
                    title: {
                      display: true,
                      text: 'Schlagfrequenz [1/min]'
                    }
                  }
                },
                plugins: {
                  title: {
                    display: true,
                    text: "Schlagfrequenz"
                  },
                  legend: {
                    onClick: (evt, legendItem, legend) => {
                       //Update boats_in_chart
                       const hidden = !legendItem.hidden;
                       state.setChartOptionBoats(hidden, legendItem.text)
                    },
                   
                },
                }
              }, {
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
                    title: {
                      display: true,
                      text: 'Vortrieb [m/Schlag]'
                    }
                  }
                },
                plugins: {
                  title: {
                    display: true,
                    text: "Vortrieb"
                  },
                  legend: {
                    onClick: (evt, legendItem, legend) => {
                       //Update boats_in_chart
                       const hidden = !legendItem.hidden;
                       state.setChartOptionBoats(hidden, legendItem.text)
                    },
                   
                },
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
                    this.data.raceData[0].chartOptions = createChartOptions(response.data.race_boats)
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
                    this.data.multiple = null
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
        resetMultiple() {
            this.data.multiple = null
        },
        setChartOptions(difference, boats) {
            if (difference != null) {
                this.data.raceData[0].chartOptions.difference_to = difference
            }
            if (boats != null) {
                 this.data.raceData[0].chartOptions.boats_in_chart = boats
            }
        },
        setChartOptionBoats(hidden, boat) {
            let boats_in_chart = this.data.raceData[0].chartOptions.boats_in_chart
            if (hidden == true && boats_in_chart.includes(boat)) {
                this.data.raceData[0].chartOptions.boats_in_chart = boats_in_chart.filter(item => item !== boat)
            }
            else if (hidden == false && !boats_in_chart.includes(boat)) {
                boats_in_chart.push(boat)
            }
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
            const csvContent ="Rennen;" + this.compData.display_name + "\n"
            + "Ort;" + this.compData.venue.replace(",", " |") + "\n"
            + "Startzeit;" + this.compData.start_date + "\n"
            + "Weltbestzeit;" + this.compData.worldBestTimeBoatClass + "\n"
            + "Bestzeit laufender OZ/Jahr;" + this.compData.bestTimeBoatClassCurrentOZ + "\n"
            + "Progression;" + progression
            + "\n\n"
            + finalData.map(e => e.join(",")).join("\n");
            createCSV(csvContent, "_" + this.compData.boat_class)
        },
        exportRaces() {
            let csvContent = [];
            const columnNames = ["Gruppe", "Nation", "Jahr", "Event", "Stadt", "Lauf", "Platzierung", "Zeit", "500m_split", "1000m_split", "1500m_split", "2000m_split"]
            csvContent.push(columnNames.join(";") + "\n")
            const groups = this.data.multiple.groups
            groups.forEach(group => {
                group.race_boats.forEach(boat => {
                    const row = []
                    row.push(group.name)
                    row.push(group.country)
                    row.push(boat.year)
                    //Mannschaft
                    row.push(boat.event)
                    //Datum
                    row.push(boat.city)
                    row.push(boat.phase)
                    row.push(boat.rank)
                    row.push(formatMilliseconds(boat.time))
                    row.push(formatMilliseconds(boat.intermediates[500]["pace [millis]"]))
                    row.push(formatMilliseconds(boat.intermediates[1000]["pace [millis]"]))
                    row.push(formatMilliseconds(boat.intermediates[1500]["pace [millis]"]))
                    row.push(formatMilliseconds(boat.intermediates[2000]["pace [millis]"]))
                    csvContent.push(Object.values(row).join(';') + "\n")
                })
            });

            createCSV(Object.values(csvContent).join(""), this.data.multiple.boat_class);
        }
       
    
    }
});
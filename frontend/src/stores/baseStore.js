import axios from "axios";
import {defineStore} from "pinia";

// function to convert milliseconds to min:sec:ms
const formatMilliseconds = ms => {
    if (typeof ms === 'number' && ms != -Infinity) {
        return new Date(ms).toISOString().slice(14, -2);
    }
    else {
        return '00:00.00'
    }   
};

function roundToTwoDecimal(num) {
    return num ? Number(num.toFixed(2)) : num;
}

function formatForExcel(num) {
    if (typeof num === 'number'  && !isNaN(num)) {
        const shortNum = roundToTwoDecimal(num)
        const stringNum = shortNum ? shortNum.toString() : '0'
        return stringNum.replace('.', ',')
    }
    else {
         return num
    }   
}

function calculatePropulsion(speed, strokeFrequency) {
    if(typeof speed === 'number' && typeof strokeFrequency === 'number' && strokeFrequency != 0 && !isNaN(strokeFrequency)) {
        return (speed * 60 / strokeFrequency)
    }
    else {
        return 0
    }

}

function getLabel(group, country) {
    return `${group} (${country})`
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
    if (firstBoat) {
        return {
        boats: boats.map(boat => boat.name),
        difference_to: firstBoat.name,
        boats_in_chart: boats.map(boat => boat.name)
        }
    }
    return null;
}

function getChartLabels(min = 0, max = 2000, steps = 500) {
    const range = []
    for(let i = min; i<= max; i+= steps) {
        range.push(i)
    }
    return range
}

function createMultipleChartOptions(groups) {
    return {
        groups: groups.map(group => getLabel(group.name, group.country)),
        showConfidenceInterval: "Anzeigen",
        confidenceIntervalOptions: ["Anzeigen", "Verbergen"],
        groups_in_chart: groups.map(group => getLabel(group.name, group.country)),
    }
}

function getChartOptions(state, title, x_title, y_title, y_reverse = false, y_stepsize, y_min, y_max, boat_chart) {
    //Returns options object
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: {
                    display: true,
                    text: x_title
                },
                grid: {
                    lineWidth: (ctx) => {
                      // Thicker lines at 500m intervals
                      const tick = ctx.tick.label;
                      return tick % 500 === 0 ? 2 : 0.5;
                    },
                },
            },
            y: {
                title: {
                    display: true,
                    text: y_title
                },
                reverse: y_reverse,
                ticks: {
                    stepSize: y_stepsize
                },
                min: y_min,
                max: y_max
            }
        },
        plugins: {
            title: {
                display: true,
                text: title
            },
        }
    }

    if (boat_chart) {
        options.plugins.legend = {
            onClick: (evt, legendItem, legend) => {
                //Update multiple.groups_in_chart
                const hidden = !legendItem.hidden;
                state.setChartOptionBoats(hidden, legendItem.text)
            }
        }
    }
    else if (!boat_chart) {
        options.plugins.legend = {
            labels: {
                filter: function (item, chart) {
                    // Show legend only for 'Dataset 1'
                    if (item.text.includes("Gruppe")) {
                        return item.datasetIndex % 3 == 0;
                    }
                    return true
                }
            },
            onClick: (evt, legendItem, legend) => {
                const hidden = !legendItem.hidden;
                legend.chart.data.datasets.forEach(dataset => {
                    if (dataset.label === legendItem.text) {
                        dataset.hidden = hidden
                    }
                });
                legend.chart.update()
                //Update multiple.groups_in_chart
                state.setMultipleChartOptionsGroups(hidden, legendItem.text)
            }
        }
    }
    return options
}


// predefined colors for charts
const COLORS = ['#0C67F7', '#93E9ED', '#E0A9FA', '#E0B696', '#E0FAAC', '#F0E95A'];
export const useRennstrukturAnalyseState = defineStore({
    id: "base",
    state: () => ({
        filterOpen: false,
        loadingState: false,
        emailLink: '',
        display: "EMPTY",
        relation_time_from: "wbt",
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
        getRaceAnalysisFilterOptions(state) {
            return state.data.filterOptions
        },
        getDisplay(state) {
            return state.display
        },
        getMultiple(state) {
            return state.data.multiple
        },
        //Competition/Events/Races
        getAnalysisData(state) {
            return state.data.analysis
        },
        //Used for general Information about Competition
        getCompetitionData(state) {
            const data = state.data.raceData[0]
            data.worldBestTimeBoatClass = formatMilliseconds(data.result_time_world_best);
            data.bestTimeBoatClassCurrentOZ = formatMilliseconds(data.result_time_best_of_current_olympia_cycle);
            state.compData = data
            return data
        },
        getBoatClassData(state) {
            if (state.data.multiple?.boat_class) {
                return {
                    "boat_class": state.data.multiple.boat_class,
                    "wbt": formatMilliseconds(state.data.multiple.world_best_time),
                    "wbt_oz": formatMilliseconds(state.data.multiple.oz_best_time),
                }
            }
            return null;
        },
        
        getOutlierCountries(state) {
            return state.outlierCountries
        },
        getLoadingState(state) {
            return state.loadingState
        },
        getRelationTimeFrom(state) {
            return state.relation_time_from
        },
        getEmailLink(state) {
            return state.emailLink
        },


        //Table data
        getMultipleTableData(state) {
            const tableData = []
            const tableHead = [
                {text: 'Gruppe', tooltip: "Gruppe (Anzahl Rennen)"},
                {text: 'Zeitraum', tooltip: null},
                {text: 'Events', tooltip: null},
                {text: 'Läufe', tooltip: "Läufe (Platzierungen)"},
                {text: 'Nation', tooltip: null},
                {text: 'Zeit', tooltip: "mm:ss; Speed"},
                {text: '500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '1000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '1500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '2000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: 'Relationszeit', tooltip: "zu ausgewähler Bestzeit"},
                {text: 'Rennstruktur', tooltip: null}
            ]
            tableData.push(tableHead)

            state.outlierCountries.clear()
            
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
                        if(totalTime != 'DNS' && totalTime != 0) {
                            const time = intermediate["time [millis]"]["mean"]
                            const rank = intermediate["rank"]["mean"]
                            const pace = intermediate["pace [millis]"]["mean"]
                            const relativePace = (pace / totalTime * 400).toFixed(1)
                            const strokeFrequency = intermediate["stroke [1/min]"] ? intermediate["stroke [1/min]"]["mean"] : 0
                            const speed = intermediate["speed [m/s]"]["mean"] ? intermediate["speed [m/s]"]["mean"]: 0
                            const propulsion = calculatePropulsion(speed, strokeFrequency)
                       
                            intermediate_values.push([
                                `${formatMilliseconds(time)} min (${rank.toFixed(1)})`,
                                `${formatMilliseconds(pace)} min (${relativePace}%)`,
                                `${strokeFrequency.toFixed(1)} spm (${propulsion.toFixed(1)} m/Schlag)`,
                                `${speed.toFixed(1)} m/s`
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
                    if(state.data.multiple.world_best_time == 0 && state.data.multiple.oz_best_time != 0) {
                        state.relation_time_from = "ozt"
                    }
                    else if(state.data.multiple.oz_best_time == 0 && state.data.multiple.world_best_time != 0)  {
                        state.relation_time_from = "wbt"
                    }
                    if(state.relation_time_from == "wbt") {
                        relationsZeit = (state.data.multiple.world_best_time / totalTime * 100).toFixed(1)
                    }
                    else {
                        relationsZeit = (state.data.multiple.oz_best_time / totalTime * 100).toFixed(1)
                    }

                    rowData.push(`${relationsZeit}%`)
                    rowData.push(group.pacing_profile)  //Rennstruktur
                }
                if (rowData.length < tableHead.length) {
                    rowData.push(...(new Array(tableHead.length - rowData.length).fill("-")))
                }
                

                tableData.push(rowData)
            }
            return tableData
        },
        getTableData(state) {
            
            const tableData = [];
            const tableHead = [
                {text: 'Platz', tooltip: null},
                {text: 'Bahn', tooltip: null},
                {text: 'Nation', tooltip: null},
                {text: 'Mannschaft', tooltip: null},
                {text: 'Zeit', tooltip: "mm:ss; Speed"},
                {text: '500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '1000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '1500m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: '2000m', tooltip: "Zeit (Platzierung); Pace (rel. Pace); Schläge/Minute (Meter/Schlag); Speed"},
                {text: 'Relationszeit', tooltip: "zu aktueller Bestzeit"},
                {text: 'Rennstruktur', tooltip: null}
            ]
            tableData.push(tableHead)

            state.outlierCountries.clear()

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

                    //Zeit
                    const totalTime = dataObj.intermediates?.[2000]?.["time [millis]"] ?? 0;
                    let averageSpeed = 0
                    if ( Number.isFinite(totalTime)) {
                        averageSpeed = 2000 * 1000 / totalTime
                    }

                    rowData.push([
                        Number.isFinite(totalTime) ? formatMilliseconds(totalTime) : totalTime,
                        `${averageSpeed.toFixed(1)} m/s`
                    ]);
                   
                    //dispalys time, rank, pace, relative pace, strokeFrequency, propulsion and speed for each 500m section
                    const intermediate_values = [];

                    for (const [index, [key, intermediate]] of Object.entries(dataObj.intermediates).entries()) {
                        if (key !== '0') {
                            if (intermediate["is_outlier"]) {
                                state.outlierCountries.add(countryIdx)
                            }
                            if(Number.isFinite(totalTime) && totalTime != 0) {
                                const time = intermediate["time [millis]"]
                                const rank = intermediate["rank"]
                                const pace = intermediate["pace [millis]"]
                                const relativePace = (pace / totalTime * 400).toFixed(1)
                                const strokeFrequency = intermediate["stroke [1/min]"] ? roundToTwoDecimal(intermediate["stroke [1/min]"]) : 0
                                const speed = intermediate["speed [m/s]"] ? roundToTwoDecimal(intermediate["speed [m/s]"]): 0
                                const propulsion = calculatePropulsion(speed, strokeFrequency)
                           
                                intermediate_values.push([
                                    `${formatMilliseconds(time)} min (${rank})`,
                                    `${formatMilliseconds(pace)} min (${relativePace}%)`,
                                    `${strokeFrequency} spm, (${propulsion.toFixed(1)} m/Schlag)`,
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
                    if (Number.isFinite(totalTime) && totalTime != 0) {
                        let relationsZeit = 0
                        if(state.relation_time_from == "wbt") {
                            relationsZeit = (state.data.raceData[0].result_time_world_best / totalTime * 100).toFixed(1)
                        }
                        else {
                            relationsZeit = (state.data.raceData[0].result_time_world_best_before_olympia_cycle / totalTime * 100).toFixed(1)
                        }
                        rowData.push(`${relationsZeit}%`)
                    }
                    else {
                        rowData.push('-')
                    }

                    //Rennstruktur
                    rowData.push(dataObj.pacing_profile)
                
                    tableData.push(rowData);
                }
            })
            return tableData;
        },


        //Data for Charts
        getDeficitInMeters(state) {
            const raceData = state.data.raceData[0]
            const raceBoats = raceData.race_boats;
            const referenceBoat = raceData.chartOptions.difference_to

            // get reference boat's data for comparison
            const winnerIdx = raceBoats.findIndex(team => team.name === referenceBoat);
            const winnerData = raceBoats.map(dataObj => dataObj.race_data)[winnerIdx];
            const winnerTeamSpeeds = Object.fromEntries(Object.entries(winnerData).map(
                ([key, val]) => [key, val["speed [m/s]"]]
            ));

            let colorIndex = 0;

            // Build datasets for each team
            const datasets = raceBoats.map((team, i) => {
                const speedData = team.race_data;
                let diffSpeedValues = {};

                const intervals = Object.keys(speedData)
                    .map((key, idx, keys) => (idx === keys.length - 1 ? 0 : keys[idx + 1] - key))
                    .filter(interval => interval !== 0);

                const counts = intervals.reduce((acc, interval) => {
                    acc[interval] = (acc[interval] || 0) + 1;
                    return acc;
                }, {});

                const interval = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b, 0);

                if (interval !== 0) {
                    let prevValue = 0;
                    Object.entries(speedData).forEach(([key, val]) => {
                        const speedWinner = winnerTeamSpeeds[key];
                        const speedCurrentTeam = val["speed [m/s]"];
                        const time = speedWinner !== 0 ? interval / speedWinner : 0;
                        if (Number(key) !== 0) {
                            prevValue = diffSpeedValues[key - interval] || 0;
                        }
                        if (speedCurrentTeam !== 0) {
                            diffSpeedValues[key] = prevValue + ((speedWinner * time) - (speedCurrentTeam * time));
                        }
                    });
                }

                // Prepare data for the current team
                const label = team.name
                const backgroundColor = COLORS[colorIndex % 6];
                const borderColor = COLORS[colorIndex % 6];
                const data = [0, ...Object.values(diffSpeedValues)]; // Add data at position 0

                const hidden = !raceData.chartOptions.boats_in_chart.includes(label);
                colorIndex++;

                return { label, backgroundColor, borderColor, data, hidden };
            });

            return {
                labels: getChartLabels(undefined, undefined, 50),  // Add 0 in x-axis
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
                    const data = Object.values(dataObj.race_data).map(obj => obj[key] === 0 ? null : obj[key])
                    var hidden = true
                    if (state.data.raceData[0].chartOptions.boats_in_chart.includes(label)) {
                        hidden = false
                    }

                    data.splice(0,0,null)           //No value at 0
                    datasets.push({label, backgroundColor, borderColor, data, hidden})
                    colorIndex++
                });
                return {
                    labels: getChartLabels(undefined, undefined, 50),
                    datasets
                };
            })
        },
        getMeanGPSChartData(state) {
            const chartDataKeys = ['speed [m/s]', 'stroke [1/min]', 'propulsion [m/stroke]']
            const dataKeys = ["mean", "lower_bound", "upper_bound"];
            return chartDataKeys.map(chartKey => {
                const datasets = []
                let colorIndex = 0

                state.data.multiple.groups.forEach(dataObj => {
                    const label = getLabel(dataObj.name, dataObj.country)

                    dataKeys.forEach(key => {
                        let backgroundColor
                        let borderColor
                        const data = Object.values(dataObj.stats_race_data).map(obj => obj[chartKey][key])
                        data.splice(0, 0, null)           //No value at 0
                        let hidden = true
                        if (key == "mean") {
                            if (state.data.multiple.chartOptions.groups_in_chart.includes(label)) {
                                hidden = false
                            }
                            backgroundColor = COLORS[colorIndex % 6];
                            borderColor = COLORS[colorIndex % 6];
                            datasets.push({ label, backgroundColor, borderColor, data, hidden });
                        }
                        else {
                            if (state.data.multiple.chartOptions.groups_in_chart.includes(label) && state.data.multiple.chartOptions.showConfidenceInterval == "Anzeigen") {
                                hidden = false
                            }
                            backgroundColor = COLORS[colorIndex % 6].concat("15");
                            borderColor = COLORS[colorIndex % 6].concat("15");
                            const pointRadius = 0
                            let fill = false
                            if (key == "upper_bound") {
                                fill = "-1"
                            }
                            datasets.push({ label, backgroundColor, borderColor, data, pointRadius, fill, hidden});
                        }
                    })
                    colorIndex++
                });
                return {
                    labels: getChartLabels(undefined, undefined, 50),
                    datasets
                };
            })
        },
        getIntermediateChartData(state) {
            const intermediateDataKeys = ["rank", "time [millis]", "rel_speed [%]"];
            // get reference boat to calculate difference
            const raceData = state.data.raceData[0];
            const raceBoats = raceData.race_boats;
            const chartOptions = raceData.chartOptions;

            const referenceBoat = chartOptions.difference_to
            const winnerIdx = raceBoats.findIndex(team => team.name === referenceBoat);
            const winnerData = raceBoats.map(dataObj => dataObj.intermediates)[winnerIdx];
            const winnerTeamTimes = Object.fromEntries(Object.entries(winnerData).map(
                ([key, val]) => [key, val["time [millis]"]]
            ));

            return intermediateDataKeys.map(key => {
                let chartLabels = getChartLabels(undefined, undefined, 500)
                const datasets = raceBoats.map((boat, index) => {
                    const label = boat.name;
                    const color = COLORS[index % 6];
                    const hidden = !chartOptions.boats_in_chart.includes(label);

                    // add zero values as start point
                    boat.intermediates["0"] = {"rank": 1, "time [millis]": 0}
                    let data = []
                    if (key == "time [millis]") {
                        //(Time - reference boat time) / 1000
                        data = Object.entries(boat.intermediates).map(([distance, value]) => (value[key] - (winnerTeamTimes[distance] ?? 0)) / 1000 );
                    }
                    else if (key == 'rank') {
                        data = Object.values(boat.intermediates).map(distanceObj => distanceObj[key]);
                    }
                    else {
                        data = Object.values(boat.intermediates).map(distanceObj => distanceObj[key]).slice(1);
                        chartLabels = getChartLabels(500, undefined, 500)
                    }
                    return {label, backgroundColor: color , borderColor: color, data, hidden};
                });
                return {
                    labels: chartLabels,
                    datasets
                };
            })
        },
        getMeanIntermediateChartData(state) {
            const datasets = [];
            let colorIndex = 0;
            const dataKeys = ["mean", "lower_bound", "upper_bound"];
            state.data.multiple.groups.forEach(group => {
                const label = getLabel(group.name, group.country);
                dataKeys.forEach(key => {
                    let backgroundColor
                    let borderColor
                    const data = Object.values(group.stats).map(obj => obj["rank"][key])
                    let hidden = true
                    if (key == "mean") {
                        if (state.data.multiple.chartOptions.groups_in_chart.includes(label)) {
                            hidden = false
                        }
                        backgroundColor = COLORS[colorIndex % 6];
                        borderColor = COLORS[colorIndex % 6];
                        datasets.push({ label, backgroundColor, borderColor, data, hidden });
                    }
                    else {
                        if (state.data.multiple.chartOptions.groups_in_chart.includes(label) && state.data.multiple.chartOptions.showConfidenceInterval == "Anzeigen") {
                            hidden = false
                        }
                        backgroundColor = COLORS[colorIndex % 6].concat("15");
                        borderColor = COLORS[colorIndex % 6].concat("15");
                        const pointRadius = 0
                        let fill = false
                        if (key == "upper_bound") {
                            fill = "-1"
                        }
                        datasets.push({ label, backgroundColor, borderColor, data, pointRadius, fill, hidden});
                    }
                })

                colorIndex++;

            })
            return {
                labels: getChartLabels(500, undefined, 500),
                datasets
            }

        },
        getMeanPacingProfiles(state) {
            const datasets = [];
            let colorIndex = 0;
            const dataKeys = ["mean", "lower_bound", "upper_bound"];
            state.data.multiple.groups.forEach(group => {
                const label = getLabel(group.name, group.country);
                dataKeys.forEach(key => {
                    let backgroundColor
                    let borderColor
                    const data = Object.values(group.stats).map(obj => obj["rel_speed [%]"][key])
                    var hidden = true
                    if (key == "mean") {
                        if (state.data.multiple.chartOptions.groups_in_chart.includes(label)) {
                            hidden = false
                        }
                        backgroundColor = COLORS[colorIndex % 6];
                        borderColor = COLORS[colorIndex % 6];
                        datasets.push({ label, backgroundColor, borderColor, data, hidden });
                    }
                    else {
                        if (state.data.multiple.chartOptions.groups_in_chart.includes(label) && state.data.multiple.chartOptions.showConfidenceInterval == "Anzeigen") {
                            hidden = false
                        }
                        backgroundColor = COLORS[colorIndex % 6].concat("15");
                        borderColor = COLORS[colorIndex % 6].concat("15");
                        const pointRadius = 0
                        let fill = false
                        if (key == "upper_bound") {
                            fill = "-1"
                        }
                        datasets.push({ label, backgroundColor, borderColor, data, pointRadius, fill, hidden});
                    }
                })

                colorIndex++;

            })
            return {
                labels: getChartLabels(500, undefined, 500),
                datasets
            }
        },
        
        //Chart options
        getChartMetadata(state) {
            const number_of_boats = state.data.raceData[0].race_boats.length;
            return [
                getChartOptions(state, "Geschwindigkeit", 'Strecke [m]', 'Geschwindigkeit [m/sek]', false, undefined, undefined, undefined, true),
                getChartOptions(state, "Vortrieb", 'Strecke [m]', 'Vortrieb [m/Schlag]', undefined, undefined, undefined, undefined, true),
                getChartOptions(state, `Differenz zu ${state.data.raceData[0].chartOptions.difference_to} in sek`, 'Strecke [m]', 'Rückstand [sek]', false, undefined, undefined, undefined, true ),
                getChartOptions(state, 'Schlagfrequenz', 'Strecke [m]', 'Schlagfrequenz [1/min]', false, undefined, undefined, undefined, true),
                getChartOptions(state, "Platzierung", 'Strecke [m]', 'Platzierung', true, 1, 1, number_of_boats, true),
                getChartOptions(state, `Differenz zu ${state.data.raceData[0].chartOptions.difference_to} in m`, 'Strecke [m]', 'Differenz [m]', false, undefined, undefined, undefined, true ),
                getChartOptions(state, 'Rennstruktur', 'Strecke [m]', 'Normalisierte Geschwindigkeit', false, undefined, undefined, undefined, true)
            ]
        },
        getMultipleChartMetadata(state) {
            return [
                getChartOptions(state, "Rennstruktur", 'Strecke [m]', 'Normalisierte Geschschwindigkeit', false, undefined, undefined, undefined, false),
                getChartOptions(state, "Vortrieb", 'Strecke [m]', 'Vortrieb [m/Schlag]', undefined, undefined, undefined, undefined, false),
                getChartOptions(state, "Platzierung", 'Strecke [m]', 'Platzierung', true, 1, 1, 6, false),
                getChartOptions(state, "Geschwindigkeit", 'Strecke [m]', 'Geschwindigkeit [m/sek]', false, undefined, undefined, undefined, false),
                getChartOptions(state, 'Schlagfrequenz', 'Strecke [m]', 'Schlagfrequenz [1/min]', false, undefined, undefined, undefined, false),
            ]
        },

        //General Chart Options (which boats/ groups are shown, confidence interval, difference_to)
        getSingleOptions(state) {
            return state.data.raceData[0].chartOptions
        },
        getMultipleOptions(state) {
            return state.data.multiple.chartOptions
        },
        
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
        async fetchCompetitionData(data) { 
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/race_analysis_filter_results`, {data})
                .then(response => {
                    this.data.analysis = response.data
                    this.display = "SINGLE"
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },

        async postMultipleFormData(data) {
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_race_boat_groups`, {data})
                .then(response => {
                    this.data.multiple = response.data
                    this.data.multiple.chartOptions = createMultipleChartOptions(response.data.groups)
                    this.display = "MULTIPLE"
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                    this.data.multiple = null;
                })
        },
        async fetchRaceData(raceId) {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_race/${raceId}/`)
                .then(response => {
                this.data.raceData[0] = response.data
                this.data.raceData[0].chartOptions = createChartOptions(response.data.race_boats)
                }).catch(error => {
                console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        setToLoadingState(bool) {
            this.loadingState = bool
        },
        setDisplay(view) {
            //EMPTY, SINGLE, MULTIPLE
            this.display = view
        },
        setEmailLink(link) {
            this.emailLink = link

        },
        setRelationTimeFrom(value) {
            this.relation_time_from = value
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
        setMultipleChartOptionsGroups(hidden, group) {
            let groups_in_chart = this.data.multiple.chartOptions.groups_in_chart
            if (hidden == true && groups_in_chart.includes(group)) {
                this.data.multiple.chartOptions.groups_in_chart = groups_in_chart.filter(item => item !== group)
            }
            else if (hidden == false && !groups_in_chart.includes(group)) {
                groups_in_chart.push(group)
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
            const splits = [500, 1000, 1500, 2000]
            const columnNames = ["Gruppe", "Nation", "Jahr", "Event", "Stadt", "Athleten", "Lauf", "Platzierung", "Zeit", "500m-Zeit", "500m-Platzierung", "500m-pace", "500m-rel. pace", "500m-spm", "500m-Vortrieb", "500m-m/s", "1000m-Zeit", "1000m-Platzierung", "1000m-pace", "1000m-rel. pace", "1000m-spm", "1000m-Vortrieb", "1000m-m/s", "1500m-Zeit", "1500m-Platzierung", "1500m-pace", "1500m-rel. pace", "1500m-spm", "1500m-Vortrieb", "1500m-m/s", "2000m-Zeit", "2000m-Platzierung", "2000m-pace", "2000m-rel. pace", "2000m-spm", "2000m-Vortrieb", "2000m-m/s"]
            csvContent.push(columnNames.join(";") + "\n")
            const groups = this.data.multiple.groups
            groups.forEach(group => {
                group.race_boats.forEach(boat => {
                    const row = []
                    let totalTime = boat.intermediates[2000]["time [millis]"]
                    row.push(group.name)
                    row.push(group.country)
                    row.push(boat.year)
                    row.push(boat.event)
                    row.push(boat.city)
                    //Athletes
                    let athletes = Object.values(boat.athletes).map(athlete => `(${athlete.boat_position}) ${athlete.first_name} ${athlete.last_name}`)
                    row.push(athletes.join(', '))
                    row.push(boat.phase_sub)
                    row.push(boat.rank)
                    row.push(formatMilliseconds(boat.time))
                    splits.forEach(split => {
                        let pace = boat.intermediates[split]["pace [millis]"]
                        let speed = boat.intermediates[split]["speed [m/s]"]
                        let strokeFrequency = boat.intermediates[split]["stroke [1/min]"]
                        row.push(formatMilliseconds(boat.intermediates[split]["time [millis]"]))
                        row.push(boat.intermediates[split]["rank"])
                        row.push(formatMilliseconds(pace))
                        row.push(formatForExcel(pace / totalTime * 400))
                        row.push(formatForExcel(strokeFrequency))
                        row.push(formatForExcel(calculatePropulsion(speed, strokeFrequency)))
                        row.push(formatForExcel(speed))
                    })
                    csvContent.push(Object.values(row).join(';') + "\n")
                })
            });

            createCSV(Object.values(csvContent).join(""), this.data.multiple.boat_class);
        }
    }
});
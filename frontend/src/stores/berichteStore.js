import axios from "axios";
import {defineStore} from "pinia";

const formatMilliseconds = ms => new Date(ms).toISOString().slice(14, -2);

export const useBerichteState = defineStore({
    id: "berichte",
    state: () => ({
        filterOpen: false,
        loading: true,
        matrixTableExport: [],
        lastFilterConfig: {
          "interval": [0, 0],
          "competition_type": "",
          "boat_class": "",
          "race_phase_type": "",
        },
        selectedBoatClass: "Alle",
        filterOptions: [{
            "years": [{"start_year": 0}, {"end_year": 0}],
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
            "competition_categories": [
                {"display_name": "OG", "id": "89346342"},
                {"display_name": "EM", "id": "89346362"},
                {"display_name": "WCh", "id": "89346362"},
                {"display_name": "WCI", "id": "89346362"},
                {"display_name": "WCII", "id": "89346362"},
                {"display_name": "WCIII", "id": "89346362"},
                {"display_name": "LS", "id": "89346362"}
            ],
            "runs": {
                "finale": [
                    {"display_name": "fa"},
                    {"display_name": "fb"},
                    {"display_name": "fc"},
                    {"display_name": "fd"},
                    {"display_name": "f..."}
                ],
                "halbfinale": [
                    {"display_name": "sa/b, sa/b/c"},
                    {"display_name": "sc/d, sd/e/f"},
                    {"display_name": "s..."}
                ],
                "viertelfinale": [
                    {"display_name": "q1-4"},
                ],
                "hoffnungslauf": null,
                "vorlauf": null,
            },
            "ranks": ["1", "2", "3", "4-6"],
        }],
        data: {
            "results": null,
            "boat_classes": null,
            "start_date": "2020-06-16 14:12:00",
            "end_date": "2022-06-16 14:12:00",
            "world_best_time_boat_class": 0,
            "best_in_period": 0,
            "mean": {
                "mm:ss,00": 0,
                "m/s": 0,
                "pace 500m": 0,
                "pace 1000m": 0
            },
            "std_dev": 43360,
            "median": 432360,
            "gradation_fastest": {
                "no_of_samples": 345,
                "time": 358360
            },
            "gradation_medium": {
                "no_of_samples": 239,
                "time": 358360
            },
            "gradation_slow": {
                "no_of_samples": 167,
                "time": 358360
            },
            "gradation_slowest": {
                "no_of_samples": 463,
                "time": 358360
            },
            "plot_data": {
                "histogram": {
                    "labels": [0],
                    "data": [0]
                },
                "histogram_mean": 0,
                "histogram_sd_low": 0,
                "histogram_sd_high": 0,
                "scatter_plot": {
                    "labels": [0],
                    "data": [0]
                },
                "scatter_1_sd_high": {
                    "labels": [0],
                    "data": [0]
                },
                "scatter_1_sd_low": {
                    "labels": [0],
                    "data": [0]
                },
                "scatter_mean": {
                    "labels": [0],
                    "data": [0]
                }
            }
        },
        matrixData: null,
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getFilterConfig(state) {
            return state.lastFilterConfig
        },
        getReportFilterOptions(state) {
            return state.filterOptions
        },
        getTableData(state) {
            return state.data
        },
        getLoadingState(state) {
            return state.loading
        },
        getMatrixTableResults(state) {
            if (state.matrixData === null) {
                return null
            }
            const dataVals = Object.values(state.matrixData)
            return dataVals.length !== 0 ? dataVals.reduce((acc, item) => acc + item["count"], 0) : 0;
        },
        getLastFilterConfig(state) {
            return state.lastFilterConfig
        },
        getMatrixTableData(state) {
            if (state.matrixData === null) {
                return null;
            }
            const subHeaders = {
                "OPEN MEN": Object.values(state.filterOptions[0].boat_classes.m.elite),
                "OPEN WOMEN": Object.values(state.filterOptions[0].boat_classes.w.elite),
                "PARA MEN": Object.values(state.filterOptions[0].boat_classes.m.para),
                "PARA WOMEN": Object.values(state.filterOptions[0].boat_classes.w.para),
                "U23 MEN": Object.values(state.filterOptions[0].boat_classes.m.u23),
                "U23 WOMEN": Object.values(state.filterOptions[0].boat_classes.w.u23),
                "U19 MEN": Object.values(state.filterOptions[0].boat_classes.m.u19),
                "U19 WOMEN": Object.values(state.filterOptions[0].boat_classes.w.u19)
            }

            let rowValues = []
            Object.entries(subHeaders).forEach(([key, value], idx) => {
                rowValues.push(key)
                for (const item of value) {
                    if (item !== undefined && item.length > 1) {
                        const data = state.matrixData[item[2]]
                        if (data !== undefined) {
                            rowValues.push([
                            item[0],
                            formatMilliseconds(Number(data["wbt"])),
                            formatMilliseconds(Number(data["mean"])),
                            formatMilliseconds(Number(data["delta"])),
                            data["count"]
                        ])
                        }
                    }
                }
            })
            state.matrixTableExport = rowValues
            return rowValues
        },
        getSelectedBoatClass(state) {
            return state.selectedBoatClass === "Alle"
        },
        getBarChartData(state) {
            if (state.data.plot_data.histogram.length === 0) {
                return null
            }
            const {labels} = state.data.plot_data.histogram;
            const {
                histogram_mean: meanValue,
                histogram_sd_low: minusOneStdv,
                histogram_sd_high: plusOneStdv
            } = state.data.plot_data;

            const finalMean = formatMilliseconds(labels.reduce((a, b) => Math.abs(b - meanValue) < Math.abs(a - meanValue) ? b : a));
            const sdLow = formatMilliseconds(labels.reduce((a, b) => Math.abs(b - minusOneStdv) < Math.abs(a - minusOneStdv) ? b : a));
            const sdHigh = formatMilliseconds(labels.reduce((a, b) => Math.abs(b - plusOneStdv) < Math.abs(a - plusOneStdv) ? b : a));
            const yMax = Math.ceil(Math.max(...Object.values(state.data.plot_data.histogram.data)) / 100) * 100;


            return {
                labels: labels.map(x => formatMilliseconds(x)),
                datasets: [
                    {
                        type: 'line',
                        backgroundColor: "red",
                        borderColor: "red",
                        borderWidth: 1.5,
                        pointRadius: 1.5,
                        tension: 0.2,
                        label: "Anzahl Boote",
                        data: state.data.plot_data.histogram.data,
                    },
                    {
                        type: 'bar',
                        backgroundColor: '#5cc5ed',
                        data: state.data.plot_data.histogram.data,
                        label: "Anzahl Boote"
                    },
                    {
                        type: 'line',
                        data: [
                            {x: sdLow, y: 0},
                            {
                                x: sdLow,
                                y: yMax
                            }],
                        label: "-1SD",
                        borderColor: "darkgrey",
                        backgroundColor: "darkgrey",
                        borderWidth: 1,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    },
                    {
                        type: 'line',
                        data: [
                            {x: finalMean, y: 0},
                            {
                                x: finalMean,
                                y: yMax
                            }],
                        label: "Mittelwert",
                        borderColor: "grey",
                        backgroundColor: "grey",
                        borderWidth: 1.5,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    },
                    {
                        type: 'line',
                        data: [
                            {x: sdHigh, y: 0},
                            {
                                x: sdHigh,
                                y: yMax
                            }],
                        label: "+1SD",
                        borderColor: "darkgrey",
                        backgroundColor: "darkgrey",
                        borderWidth: 1,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    }
                ]
            }
        },
        getBarChartOptions(state) {
            return {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        min: 0,
                        title: {
                            display: true,
                            text: 'Zeit [mm:ss:ms]'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: Math.ceil(Math.max(...Object.values(state.data.plot_data.histogram.data)) / 100) * 100,
                        title: {
                            display: true,
                            text: 'Anzahl Rennen'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: `${state.data.boat_classes} (n = ${state.data.results})`
                    }
                }
            }
        },
        getScatterChartData(state) {
            const {
                scatter_plot: scatterData,
                scatter_1_sd_high: scatter1SDHigh,
                scatter_1_sd_low: scatter1SDLow,
                scatter_mean: scatterMeanValues
            } = state.data.plot_data;

            function computeData(data, labels, targetData) {
                    return labels.map((label, i) => ({
                    x: new Date(label),
                    y: formatMilliseconds(data.reduce((a, b) =>
                        Math.abs(b - targetData.data[i]) < Math.abs(a - targetData.data[i]) ? b : a))
                }));
            }

            const plotData = scatterData.labels.map((label, i) => ({
                x: new Date(label),
                y: formatMilliseconds(scatterData.data[i])
            }));
            const sd1Low = computeData(scatterData.data, scatter1SDLow.labels, scatter1SDLow);
            const sd1High = computeData(scatterData.data, scatter1SDHigh.labels, scatter1SDHigh);
            const meanValues = computeData(scatterData.data, scatterMeanValues.labels, scatterMeanValues);

            return {
                datasets: [
                    {
                        type: 'scatter',
                        data: plotData,
                        label: "Einzelergebnisse",
                        backgroundColor: '#5cc5ed',
                        borderColor: '#5cc5ed'
                    },
                    {
                        type: 'line',
                        data: sd1Low,
                        label: "-1SD",
                        borderColor: "darkgrey",
                        backgroundColor: "darkgrey",
                        borderWidth: 1,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    },
                    {
                        type: 'line',
                        data: meanValues,
                        label: "Mittelwert",
                        borderColor: "grey",
                        backgroundColor: "grey",
                        borderWidth: 1.5,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    },
                    {
                        type: 'line',
                        data: sd1High,
                        label: "+1SD",
                        borderColor: "darkgrey",
                        backgroundColor: "darkgrey",
                        borderWidth: 1,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                    }
                ]
            }
        },
        getScatterChartOptions(state) {
            return {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            parser: 'yyyy–mm–dd'
                        },
                        title: {
                            display: true,
                            text: 'Jahr'
                        }
                    },
                    y: {
                        type: 'time',
                        reverse: true,
                        time: {
                            parser: 'HH:mm:ss',
                            unit: "seconds",
                            tooltipFormat: 'HH:mm:ss',
                            displayFormats: {
                                'seconds': "HH:mm:ss"
                            },
                            unitStepSize: 30
                        },
                        title: {
                            display: true,
                            text: 'Zeit [mm:ss.ms]'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                    },
                    title: {
                        display: true,
                        text: `${String(state.data.boat_classes)} (n = ${state.data.results})`
                    }
                }
            }
        }
    },
    actions: {
        async fetchReportFilterOptions() {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_report_filter_options`)
                .then(response => {
                    this.filterOptions = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postFormData(data) {
            this.loading = true
            this.selectedBoatClass = data.boat_classes
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_report_boat_class`, {data})
                .then(response => {
                    this.data = response.data
                    this.loading = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postFormDataMatrix(data) {
            this.selectedBoatClass = "Alle"
            this.loading = true
            await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/matrix`, {data})
                .then(response => {
                    this.matrixData = response.data
                    this.loading = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        setSelectedBoatClass(boat_class) {
            this.selectedBoatClass = boat_class
        },
        setLastFilterConfig(filterConfig) {
            this.lastFilterConfig = filterConfig
        },
        setFilterConfig(data) {
            this.filterConfig = data
        },
        exportMatrixTableData() {
            var results = 0;

            if(this.data.results > 0) {
                results = this.data.results;
            } else {
                results = 0;
            }

            const csvContent = "data:text/csv;charset=utf-8,"
                + "Bootsklassen,Alle\n"
                + "Datensätze," + results + "\n"
                + "Zeitraum," + this.lastFilterConfig.interval[0] + " - " + this.lastFilterConfig.interval[1] + "\n"
                + "Events," + this.lastFilterConfig.competition_type.replaceAll(",", " |") + "\n"
                + "Läufe," + this.lastFilterConfig.race_phase_type.replaceAll(",", " |") + "\n"
                + "Läufe (erweitert)," + this.lastFilterConfig.race_phase_subtype.replaceAll(",", " |") + "\n\n"
                
                + ",WB [t],Ø [t],Δ [s],n\n"
                + this.matrixTableExport.map(row => {
                    if (Array.isArray(row)) {
                        return row.map(cell => {
                            if (typeof cell === "string") {
                                return `"${cell}"`;
                            }
                            return cell;
                        }).join(",");
                    }
                    return row;
                }).join("\n");
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Berichte_" + "Matrix.csv");
            document.body.appendChild(link);
            link.click();
        },
        exportBoatClassTableData() {
            var results = 0;
            var worldbesttime = 0;

            if(this.data.results > 0) {
                results = this.data.results;
            } else {
                results = 0;
            }

            if(this.data.world_best_time_boat_class > 0) {
                worldbesttime = formatMilliseconds(this.data.world_best_time_boat_class)
            } else {
                worldbesttime = "-"
            }
            
            const csvContent = "data:text/csv;charset=utf-8,"
                + "Bootsklasse," + this.data.boat_classes + "\n"
                + "Datensätze," + this.data.results + "\n"
                + "Zeitraum," + this.lastFilterConfig.interval[0] + " - " + this.lastFilterConfig.interval[1] + "\n"
                + "Events," + this.lastFilterConfig.competition_type.replaceAll(",", " |") + "\n"
                + "Läufe," + this.lastFilterConfig.race_phase_type.replaceAll(",", " |") + "\n"
                + "Läufe (erweitert)," + this.lastFilterConfig.race_phase_subtype.replaceAll(",", " |") + "\n\n"

                + "Weltbestzeit," + worldbesttime + "\n"
                + "Beste im Zeitraum," + formatMilliseconds(this.data.best_in_period) + "\n"
                + "Ø Geschwindigkeit (m/s)," + this.data["mean"]["m/s"] + "\n"
                + "Ø t über 500m," + formatMilliseconds(this.data["mean"]["pace 500m"]) + "\n"
                + "Ø t über 1000m," + formatMilliseconds(this.data["mean"]["pace 1000m"]) + "\n"
                + "Ø t über 2000m," + formatMilliseconds(this.data["mean"]["mm:ss,00"]) + "\n"
                + "Standardabweichung," + formatMilliseconds(this.data.std_dev) + "\n"
                + "Median," + formatMilliseconds(this.data.median) + "\n"
                + ",Bedingungen\n"
                + "Abstufung schnellste," + "(n=" + this.data["gradation_fastest"]["results"] + ") " + formatMilliseconds(this.data["gradation_fastest"]["time"]) + "\n"
                + "Abstufung mittel," + "(n=" + this.data["gradation_medium"]["results"] + ") " + formatMilliseconds(this.data["gradation_medium"]["time"]) + "\n"
                + "Abstufung langsam," + "(n=" + this.data["gradation_slow"]["results"] + ") " + formatMilliseconds(this.data["gradation_slow"]["time"]) + "\n"
                + "Abstufung langsamste," + "(n=" + this.data["gradation_slowest"]["results"] + ") " + formatMilliseconds(this.data["gradation_slowest"]["time"]);
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Berichte_" + this.data.boat_classes + ".csv");
            document.body.appendChild(link);
            link.click();
        }
    }
})

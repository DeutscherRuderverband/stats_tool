import axios from "axios";
import {defineStore} from "pinia";

const COLORS = [
    '#2d8bcf', '#dfc1b6', '#73dee9',
    '#ff7f7f', '#ffa97f', '#7fffaf',
    '#7fff7f', '#e099f9', '#e0faad',
    '#e0a079', '#897373', '#7fffbe',
    '#f5ed5f', '#918e7f', '#c6b09e',
    '#9f7fff', '#262626', '#bdbdbd'
]


export const useMedaillenspiegelState = defineStore({
    id: "medaillenspiegel",
    state: () => ({
        filterOpen: false,
        loading: true,
        tableExport: [],
        filterOptions: [{
            "years": [{"start_year": ""}, {"end_year": ""}],
            "boat_classes": {},
            "competition_categories": [{"":""}],
            "nations": {"": ""},
            "medal_types": [{"":""}]
        }],
        data: {
                "results": 0,
                "start_date": 0,
                "end_date": 0,
                "comp_types": [],
                "category": 0,
                "boat_classes": [],
                "data": []
            }
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getMedaillenspiegelFilterOptions(state) {
            return state.filterOptions
        },
        getFilterSelection(state) {
            return state.data
        },
        getLoadingState(state) {
            return state.loading
        },
        getTableData(state) {
            let tableData = [["Platz", "Nation", "Gold", "Silber", "Bronze", "Medaillen", "Platz 4-6", "Finale A", "Finale B"]];
            const valueKeys = ["rank", "nation", "gold", "silver", "bronze", "total", "four_to_six", "final_a", "final_b"];
            const data = state.data.data
            for (const el of data) {
                let temp1Array = []
                for (const valueKey of valueKeys) {
                    temp1Array.push(el[valueKey]);
                }
                tableData.push(temp1Array)
            }
            state.tableExport = tableData
            return tableData
        },
        getBarChartData(state) {
            const data = state.data.data
            let dataSets = []
            const labels = ["Gold", "Silver", "Bronze", "Total"]
            for (const [index, country] of data.entries()) {
                dataSets.push({
                    type: 'bar',
                    label: country.nation,
                    backgroundColor: COLORS[index % COLORS.length],
                    data: [country.gold, country.silver, country.bronze, country.total]
                })
            }
            return {
                labels: labels,
                datasets: dataSets
            }
        },
    },
    actions: {
        async fetchMedaillenspiegelFilterOptions() {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_medals_filter_options`)
                .then(response => {
                    this.filterOptions = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        async postFormData(data) {
            this.loading = true
             await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_medals`, {data})
                .then(response => {
                    this.data = response.data
                    this.loading = false
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        exportTableData() {
            const csvContent = "data:text/csv;charset=utf-8,"
                + "Datensätze," + this.data.results + "\n"
                + "Zeitraum," + this.data.start_date + " - " + this.data.end_date + "\n"
                + "Events," + this.data.comp_types.replaceAll(",", " |")
                + "\n\n"
                + this.tableExport.map(e => e.join(",")).join("\n")
            ;
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Medaillenspiegel.csv");
            document.body.appendChild(link);
            link.click();
        }
    }
})

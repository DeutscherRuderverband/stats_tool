import axios from "axios";
import {defineStore} from "pinia";

const COLORS = ['#0C67F7', '#93E9ED', '#E0A9FA', '#E0B696', '#E0FAAC', '#F0E95A'];

export const useMedaillenspiegelState = defineStore({
    id: "medaillenspiegel",
    state: () => ({
        filterOpen: false,
        tableExport: [],
        filterOptions: [{
            "years": [{"start_year": ""}, {"end_year": ""}],
            "boat_classes": {},
            "competition_categories": [{"":""}],
            "nations": {"": ""},
            "medal_types": [{"":""}]
        }],
        data: {
                "results": 1,
                "start_date": 0,
                "end_date": 0,
                "events": null,
                "category": null,
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
        getTableData(state) {
            let tableData = [["Platz", "Nation", "Punkte", "Gold", "Silber", "Bronze", "Gesamt", "Finale A", "Finale B"]];
            const valueKeys = ["rank", "nation", "points", "gold", "silver", "bronze", "total", "final_a", "final_b"];
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
             await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_medals`, {data})
                .then(response => {
                    this.data = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        exportTableData() {
            const csvContent = "data:text/csv;charset=utf-8," + this.tableExport.map(e => e.join(",")).join("\n");
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "medaillenspiegel.csv");
            document.body.appendChild(link);
            link.click();
        }
    }
})

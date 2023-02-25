import axios from "axios";
import {defineStore} from "pinia";

export const useHomeStore = defineStore({
    id: "home",
    state: () => ({
        data: {
            calender_data: []
        },
        legend: {}
    }),
    getters: {
        getCalenderData(state) {
            let calenderEntries = state.data.calender_data;
            const color_scheme = {
                "Paralympics": "#1f77b4",
                "World Rowing Cup": "#aec7e8",
                "World Rowing Championships": "#2ca02c",
                "World Rowing U23 Championships": "#98df8a",
                "Olympics": "#1c5b7d",
                "Masters": "#bcbd22",
                "World Rowing Under 19 Championships": "#17becf",
                "Indoor Championships": "#9edae5",
                "Continental Championships": "#3182bd",
                "International Regattas": "#6baed6",
                "Coastal Championships": "#2171b5",
                "Other World Rowing Competitions": "#c6dbef",
                "World Rowing Combined Championships": "#6baed6"
            }
            return calenderEntries.map((entry, index) => {
                const hexCode = color_scheme[entry.comp_type]
                state.legend[entry.comp_type] = hexCode
                entry.customData["style"] = 'background-color:' + hexCode;
                return entry;
            });
        },
        getCalenderLegend(state) {
            return state.legend
        }
    },
    actions: {
        async fetchCalendarData(year) {
            try {
                const response = await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/calendar/${year}`);
                this.data.calender_data = response.data;
            } catch (error) {
                console.error(error);
            }
        }
    }
});
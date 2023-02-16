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
                "Paralympics": "#ff7f00",
                "World Rowing Cup": "#b3de69",
                "World Rowing Championships": "#a65628",
                "World Rowing U23 Championships": "#f781bf",
                "Olympics": "#377eb8",
                "Masters": "#ffff33",
                "World Rowing Under 19 Championships": "#e41a1c",
                "Indoor Championships": "#a6cee3",
                "Continental Championships": "#4daf4a",
                "International Regattas": "#fdbf6f",
                "Coastal Championships": "#bebada",
                "Other World Rowing Competitions": "#8dd3c7",
                "World Rowing Combined Championships": "#984ea3"
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
import axios from "axios";
import { defineStore } from "pinia";

export const useTeamsState = defineStore({
    id: "teams",
    state: () => ({
        filterOpen: false,
        tableExport: [],
        filterOptions: [{
            "years": [{ "start_year": "" }, { "end_year": ""}],
            "competition_categories": [{"": ""}],
            "nations": {},
        }],
        data: [{
                "year": [{ "start_year": 1950 }, { "end_year": 2025 }],
                "nation_ioc": "GER",
                "results": 127973,
                "men": {
                    "junior": {
                        "single": {
                            "JM1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "double": {
                            "JM2x": [
                                {
                                    "id": 1113333,
                                    "firstName": "Kay",
                                    "lastName": "Winkert"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "quad": {
                            "JM4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "pair": {
                            "JM2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "coxed_four": {
                            "JM4+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "four": {
                            "JM4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "eight": {
                            "JM8-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        }
                    },
                    "u19": {
                    },
                    "u23": {
                        "single": {
                            "BM1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "double": {
                            "BM2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "quad": {
                            "BM4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "pair": {
                            "BM2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "coxed_four": {
                            "BM4+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "four": {
                            "BM4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "eight": {
                            "BM8+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_single": {
                            "BLM1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_double": {
                            "BLM2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_quad": {
                            "BLM4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_pair": {
                            "BLM2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        }
                    },
                    "adult": {
                        "single": {
                            "M1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "double": {
                            "M2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "quad": {
                            "M4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "pair": {
                            "M2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "four": {
                            "M4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "eight": {
                            "M8+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_single": {
                            "LM1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_double": {
                            "LM2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_quad": {
                            "LM4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "lw_pair": {
                            "LM2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        }
                    },
                    "pr": {
                        "1": {
                            "PR1 M1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Kai",
                                    "lastName": "Winkert"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "2": {
                            "PR2 M1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        },
                        "3": {
                            "PR3 M2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                }
                            ]
                        }
                    }
                },
                "women": {
                    "junior": {
                        "single": {
                            "JW1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "double": {
                            "JW2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "quad": {
                            "JW4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "pair": {
                            "JW2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "coxed_four": {
                            "JW4+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "four": {
                            "JW4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "eight": {
                            "JW8-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        }
                    },
                    "u19": {
                    },
                    "u23": {
                        "single": {
                            "BW1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "double": {
                            "BW2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "quad": {
                            "BW4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "pair": {
                            "BW2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "coxed_four": {
                            "BW4+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "four": {
                            "BW4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "eight": {
                            "BW8+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_single": {
                            "BLW1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_double": {
                            "BLW2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_quad": {
                            "BLW4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_pair": {
                            "BLW2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        }
                    },
                    "adult": {
                        "single": {
                            "W1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "double": {
                            "W2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "quad": {
                            "W4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "pair": {
                            "W2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "four": {
                            "W4-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "eight": {
                            "W8+": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_single": {
                            "LW1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_double": {
                            "LW2x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_quad": {
                            "LW4x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "lw_pair": {
                            "LW2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        }
                    },
                    "pr": {
                        "1": {
                            "PR1 W1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "2": {
                            "PR2 W1x": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        },
                        "3": {
                            "PR3 W2-": [
                                {
                                    "id": 1111111,
                                    "firstName": "Jan",
                                    "lastName": "Kuster"
                                },
                                {
                                    "id": 2222222,
                                    "firstName": "Markus",
                                    "lastName": "Last"
                                },
                            ]
                        }
                    }
                },
                "mixed": {
                    "double_2": {
                        "PR2 Mix2x": [
                            {
                                "id": 1111111,
                                "firstName": "Jan",
                                "lastName": "Kuster"
                            },
                            {
                                "id": 2222222,
                                "firstName": "Markus",
                                "lastName": "Last"
                            },
                        ]
                    },
                    "double_3": {
                        "PR3 Mix2x": [
                            {
                                "id": 1111111,
                                "firstName": "Jan",
                                "lastName": "Kuster"
                            },
                            {
                                "id": 2222222,
                                "firstName": "Markus",
                                "lastName": "Last"
                            },
                        ]
                    },
                    "four": {
                        "PR3 Mix4+": [
                            {
                                "id": 1111111,
                                "firstName": "Jan",
                                "lastName": "Kuster"
                            },
                            {
                                "id": 2222222,
                                "firstName": "Markus",
                                "lastName": "Last"
                            },
                        ]
                    }
                }
            }
        ]
    }),
    getters: {
        getFilterState(state) {
            return state.filterOpen
        },
        getTeamsFilterOptions(state) {
            return state.filterOptions
        },
        getMetaData(state) {
            return state.data[0]
        },
        getTableData(state) {
            const subHeaders = {
                "OPEN MEN": Object.values(state.data[0].men.adult),
                "OPEN WOMEN": Object.values(state.data[0].women.adult),
                "PARA MEN": Object.values(state.data[0].men.pr),
                "PARA WOMEN": Object.values(state.data[0].women.pr),
                "U23 MEN": Object.values(state.data[0].men.u23),
                "U23 WOMEN": Object.values(state.data[0].women.u23),
                "U19 MEN": Object.values(state.data[0].men.u19),
                "U19 WOMEN": Object.values(state.data[0].women.u19)
            }
            let rowValues = []
            Object.entries(subHeaders).forEach(([key, value], idx) => {
                rowValues.push(key)
                for (const item of value) {
                    let members = []
                    const itemList = Object.values(item)
                    itemList.forEach((value, idx) => {
                        value.forEach(entry => {
                            members.push(entry.firstName + " " + entry.lastName)
                        })
                    })
                    rowValues.push([Object.keys(item)[0], members])
                }
            })
            state.tableExport = rowValues
            return rowValues
        }
    },
    actions: {
        async fetchTeamsFilterOptions() {
            await axios.get(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/get_teams_filter_options`)
                .then(response => {
                    this.filterOptions = response.data
                }).catch(error => {
                    console.error(`Request failed: ${error}`)
                })
        },
        setFilterState(filterState) {
            this.filterOpen = !filterState
        },
        exportTableData() {
             const csvContent = "data:text/csv;charset=utf-8," + this.tableExport.map(row => {
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
            link.setAttribute("download", "teams.csv");
            document.body.appendChild(link);
            link.click();
        }
    }
})
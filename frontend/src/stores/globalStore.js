import {defineStore} from "pinia";

export const useGlobalState = defineStore({
  id: "global",
    state: () => ({
      headerReduced: false
    }),
    getters: {
      getHeaderReducedState(state) {
          return state.headerReduced;
      },
    },
    actions: {
      setHeaderReducedState(val) {
        this.headerReduced = val
      }
    }
})
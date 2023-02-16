<script setup>
import TeamsFilter from "@/components/filters/teamsFilter.vue";
import 'chartjs-adapter-moment';
import {Chart as ChartJS, LinearScale, PointElement, Tooltip, Legend, TimeScale} from "chart.js";
ChartJS.register(LinearScale, PointElement, Tooltip, Legend, TimeScale);
</script>

<template>
  <v-btn color="blue"
         @click="setFilterState()" v-show="!filterOpen"
        :class="mobile ? 'filterToggleButtonMobile mt-6 pa-0 ma-0' : 'filterToggleButton mt-6 pa-0 ma-0'"
         :height="mobile ? 100: 180"
         size="x-small"
  >
  <p style="writing-mode: vertical-rl; font-size: 16px; transform: rotate(180deg);">
    <v-icon style="transform: rotate(180deg); font-size: 14px; padding-left: 6px; padding-top: 10px;">mdi-filter</v-icon>
    FILTER</p>
  </v-btn>
  <v-card style="box-shadow: none; z-index: 1">
      <v-layout>
        <v-navigation-drawer
          v-model="filterOpen"
          temporary
          v-bind:style='{"margin-top" : (mobile? "71.25px" : "158px" )}'
          style="background-color: white; border: none"
          width="600">
         <teams-filter/>
        </v-navigation-drawer>

  <v-container :class="mobile ? 'px-5 py-0 main-container' : 'px-10 py-0 main-container'">
    <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
    <h1>Teams</h1>
      <v-icon id="tooltip-teams-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline</v-icon>
      <v-tooltip
          activator="#tooltip-teams-icon"
          location="end"
          open-on-hover
      >Hier findest du die Zusammensetzung der gewählten Nationalmannschaft
          mit Besetzung der Bootsklassen.
      </v-tooltip>
      <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
      <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
    </v-col>
    <v-divider></v-divider>
    <v-container class="pa-0 mt-2 pb-8" style="min-height: 400px">
      <v-row>
        <v-col cols="12">
          <h2>{{ metaData.nation_ioc }}</h2>
          <v-col cols="6" class="pa-0">
            <v-alert type="success" variant="tonal" class="my-2" v-if="metaData.results">
                <v-row>
                  <v-col cols="12">
                    <p> {{ metaData.results }} Datensätze |
                      Von {{ Object.values(metaData["year"][0])[0] }} Bis {{ Object.values(metaData["year"][1])[0] }}</p>
                  </v-col>
                </v-row>
              </v-alert>
              <v-alert type="error" variant="tonal" class="my-2" v-else>
                <v-row>
                  <v-col cols="12">
                    <p>Leider keine Ergebnisse gefunden.</p>
                  </v-col>
                </v-row>
              </v-alert>
            </v-col>
            
            <v-col cols="6" class="pa-0">
            <v-table class="tableStyles" density="compact">
                <tbody class="nth-grey">
                  <template v-for="row in tableData">
                    <tr v-if="(typeof row === 'string')" class="subheader">
                      <th><b>{{ row }}</b></th>
                      <td></td>
                    </tr>
                    <tr v-else>
                      <template v-for="item in row">
                        <td v-if="(typeof item === 'string')">{{ item }}</td>
                        <td v-else>
                          <p>
                            <template v-for="athlete, idx in item">
                              <template v-if="idx < item.length - 1">
                                {{ athlete }},
                              </template>
                              <template v-else>
                                {{ athlete }}
                              </template>
                            </template>
                          </p>
                        </td>
                      </template>
                    </tr>
                  </template>
                </tbody>
              </v-table>
              </v-col>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
      </v-layout>
  </v-card>
</template>

<script>
import { mapState } from "pinia";
import { useTeamsState } from "@/stores/teamsStore";
import {useRennstrukturAnalyseState} from "@/stores/baseStore";

export default {
  computed: {
    ...mapState(useTeamsState, {
      filterState: "getFilterState"
    }),
    ...mapState(useTeamsState, {
      metaData: "getMetaData"
    }),
    ...mapState(useTeamsState, {
      tableData: "getTableData"
    })
  },
  methods: {
    openPrintDialog() {
      window.print();
    },
     exportTableData() {
      const store = useTeamsState()
      store.exportTableData()
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useTeamsState()
      store.setFilterState(this.filterState)
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth <= 750
      let navbarHeight = window.innerWidth < 750 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },
  data() {
    return {
      mobile: false,
      filterOpen: false,
    }
  },
  watch: {
    filterState(newValue) {
      this.filterOpen = newValue;
    },
    filterOpen: function (newVal, oldVal) {
      if (oldVal === true && newVal === false && this.filterState === true) {
        const store = useTeamsState()
        store.setFilterState(oldVal)
      }
    }
  }
}
</script>

<style lang="scss" scoped>

.tableStyles {
  border: 1px solid #e0e0e0;

  th {
    border: 0.5px solid #e0e0e0;
    font-size: 14px !important;
    text-align: left;
  }

  td {
    text-align: left;
    border: 0.5px solid #e0e0e0;
  }
}

.nth-grey tr:nth-child(odd) {
  background-color: rgba(0, 0, 0, .05);
}
.distance {
  display: inline-block;
  padding-right: 10px;
}
.filterToggleButton {
  position: fixed;
  z-index: 10;
  left: 0;
  border-radius: 0 5px 5px 0;
  color: #1369b0;
}
.filterToggleButtonMobile {
  position: fixed;
  z-index: 10;
  left: 0;
  border-radius: 0 5px 5px 0;
  color: #1369b0;
  bottom: 10px;
}
.main-container {
  min-height: calc(100vh - (var(--navbar-height)) - 95px);
}

@media print {
  i, .filterToggleButton, .filterToggleButtonMobile {
    display: none;
  }
}
</style>

<template>
  <v-btn color="blue"
         @click="setFilterState()" v-show="!filterOpen"
         :class="mobile ? 'filterToggleButtonMobile mt-6 pa-0 ma-0' : 'filterToggleButton mt-6 pa-0 ma-0'"
         :height="mobile ? 100: 180"
         size="x-small"
  >
    <p style="writing-mode: vertical-rl; font-size: 16px; transform: rotate(180deg);">
      <v-icon style="transform: rotate(180deg); font-size: 14px; padding-left: 6px; padding-top: 10px;">mdi-filter
      </v-icon>
      FILTER
    </p>
  </v-btn>
  <v-card style="box-shadow: none; z-index: 1">
    <v-layout>
      <v-navigation-drawer
          v-model="filterOpen"
          temporary
          v-bind:style='{"margin-top": (mobile ? "71.25px" : (headerReduced ? "81px" : "159px"))}'
          style="background-color: white; border: none"
          width="600">
        <medaillenspiegel-filter/>
      </v-navigation-drawer>
      <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">

        <v-col :cols="mobile ? 12 : 6" class="d-flex flex-row px-0" style="align-items: center">
          <h1>Medaillenspiegel</h1>
          <v-icon id="tooltip-analysis-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline
          </v-icon>
          <v-tooltip
              activator="#tooltip-analysis-icon"
              location="end"
              open-on-hover
          >Im Rahmen des Medaillenspiegels können die Erfolge von Nationen betrachtet werden.<br>
            Zur Präzisierung der Ansicht kann aus den vorhandenen Einstellmöglichkeiten des Filters (links) gewählt werden.
          </v-tooltip>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
        </v-col>
        <v-divider></v-divider>

        <v-container v-if="loading" class="d-flex flex-column align-center">
          <v-progress-circular indeterminate color="blue" size="40" class="mt-15"></v-progress-circular>
          <div class="text-center" style="color: #1369b0">Lade Ergebnisse...</div>
        </v-container>

        <v-container class="pa-0" v-else>
          <v-row class="ma-0">
            <v-col cols="12" class="pa-0">
              <v-col :cols="mobile ? 12 : 8" class="pa-0">
                <v-alert type="success" variant="tonal" class="my-2" v-if="filterSelection.results">
                  <v-row>
                    <v-col>
                      <p><b>{{
                          `${filterSelection.results} Datensätze | Von ${filterSelection.start_date} bis ${filterSelection.end_date}`
                        }}</b></p>
                      <p><b>Events:</b> {{ filterSelection.comp_types }}</p>
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
              <v-table class="tableStyles mb-4" density="compact" v-if="filterSelection.results">
                <tbody class="nth-grey">
                <template v-for="(el, idx) in tableData">
                  <tr>
                    <template v-for="item in el">
                      <td v-if="idx === 0"><b>{{ item }}</b></td>
                      <td v-else>{{ item }}</td>
                    </template>
                  </tr>
                </template>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
          <v-col cols="12" class="pa-0" v-if="filterSelection.results">
            <v-container class="chart-bg pa-0">
              <BarChart :data="medalChartData" :chartOptions="medalChartOptions"></BarChart>
            </v-container>
          </v-col>
        </v-container>
      </v-container>
    </v-layout>
  </v-card>
</template>

<script setup>
import MedaillenspiegelFilter from "@/components/filters/medaillenspiegelFilter.vue";
import BarChart from "@/components/charts/BarChart.vue";
</script>

<script>
import {mapState} from "pinia";
import {useMedaillenspiegelState} from "@/stores/medaillenspiegelStore";
import {useGlobalState} from "@/stores/globalStore";

export default {
  computed: {
    ...mapState(useGlobalState, {
      headerReduced: "getHeaderReducedState"
    }),
    ...mapState(useMedaillenspiegelState, {
      filterState: "getFilterState"
    }),
    ...mapState(useMedaillenspiegelState, {
      medalChartData: "getBarChartData"
    }),
    ...mapState(useMedaillenspiegelState, {
      filterState: "getFilterState"
    }),
    ...mapState(useMedaillenspiegelState, {
      filterSelection: "getFilterSelection"
    }),
    ...mapState(useMedaillenspiegelState, {
      tableData: "getTableData"
    }),
    ...mapState(useMedaillenspiegelState, {
      loading: "getLoadingState"
    }),
  },
  methods: {
    openPrintDialog() {
      window.print();
    },
    exportTableData() {
      const store = useMedaillenspiegelState()
      store.exportTableData()
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useMedaillenspiegelState()
      store.setFilterState(this.filterState)
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  data() {
    return {
      mobile: false,
      filterOpen: false,
      medalChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Medaillenverteilung'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Anzahl Medaillen'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          },
          title: {
            display: true,
            text: "Medaillenspiegel Übersicht"
          }
        }
      }
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },
  watch: {
    filterState(newValue) {
      this.filterOpen = newValue;
    },
    filterOpen: function (newVal, oldVal) {
      if (oldVal === true && newVal === false && this.filterState === true) {
        const store = useMedaillenspiegelState()
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

.nth-grey tr:nth-child(even) {
  background-color: rgba(0, 0, 0, .05);
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

.chart-bg {
  background-color: #fbfbfb;
  border-radius: 3px;
}

.main-container {
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}

@media print {
  i, .filterToggleButton, .filterToggleButtonMobile {
    display: none;
  }
}
</style>

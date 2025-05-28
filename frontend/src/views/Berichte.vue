<script setup>
import ScatterChart from '@/components/charts/ScatterChart.vue';
import BarChart from "@/components/charts/BarChart.vue";
import BerichteFilter from "@/components/filters/berichteFilter.vue";
import 'chartjs-adapter-moment';
import { Chart as ChartJS, LinearScale, PointElement, Tooltip, Legend, TimeScale } from "chart.js";

ChartJS.register(LinearScale, PointElement, Tooltip, Legend, TimeScale);
</script>

<template>
  <v-btn color="blue" @click="setFilterState()" v-show="!filterOpen"
    :class="mobile ? 'filterToggleButtonMobile mt-6 pa-0 ma-0' : 'filterToggleButton mt-6 pa-0 ma-0'"
    :height="mobile ? 100 : 180" size="x-small">
    <p style="writing-mode: vertical-rl; font-size: 16px; transform: rotate(180deg);">
      <v-icon style="transform: rotate(180deg); font-size: 14px; padding-left: 6px; padding-top: 10px;">mdi-filter
      </v-icon>
      FILTER
    </p>
  </v-btn>
  <v-card style="box-shadow: none; z-index: 1">
    <v-layout>
      <v-navigation-drawer v-model="filterOpen" temporary :style="{
        marginTop: mobile ? '71.25px' : (headerReduced ? '81px' : '159px'),
        height: mobile
          ? 'calc(100vh - 71.25px)'
          : (headerReduced ? 'calc(100vh - 81px)' : 'calc(100vh - 159px)'),
        overflowY: 'auto',
        backgroundColor: 'white',
        border: 'none'
      }" width="600">
        <berichte-filter />
      </v-navigation-drawer>

      <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 py-0 main-container'">
        <!-- Heading -->
        <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
          <h1>Berichte</h1>
          <v-icon id="tooltip-analysis-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline
          </v-icon>
          <v-tooltip activator="#tooltip-analysis-icon" location="end" open-on-hover>Auf der Seite Berichte lassen sich
            Analysen über längere Zeiträume und weitere Filterkriterien erstellen.
          </v-tooltip>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon v-if="currentView == 'Alle'" @click="exportMatrixTableData()" color="grey"
            class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
          <v-icon v-if="currentView != 'Alle' &&  currentView != 'Empty' && currentView != 'Matrix'" @click="exportBoatClassTableData()"
            color="grey" class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
        </v-col>
        <v-divider></v-divider>

        <v-container v-if="loading" class="d-flex flex-column align-center">
          <v-progress-circular indeterminate color="blue" size="40" class="mt-15"></v-progress-circular>
          <div class="text-center" style="color: #1369b0">Lade Ergebnisse...</div>
        </v-container>

        <v-container class="pa-0 mt-2 pb-8" v-else>
          <!-- Empty -->
          <div v-if="currentView=='Empty'">
            <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
              Bitte wähle einen Zeitraum und Events in dem Filter auf der linken Seite.
            </v-alert>
          </div>
          <div v-else>

            <!-- Single Boat Class -->
            <v-row v-if="currentView != 'Alle' && currentView != 'Matrix'">
              <v-col :cols="mobile ? 12 : 5" class="py-0 pt-1">
                <h2>{{ tableData.boat_classes }}</h2>

                <v-alert type="error" variant="tonal" class="my-2" v-if="tableData.results === 0">
                  <v-row>
                    <v-col cols="12">
                      <p>Leider keine Ergebnisse gefunden.</p>
                    </v-col>
                  </v-row>
                </v-alert>

                <v-alert type="success" variant="tonal" class="my-2" v-else>
                  <v-row>
                    <v-col cols="12">
                      <p><b>{{tableData.results }} Datensätze |
                          Von {{ filterConf.interval[0] }} bis {{ filterConf.interval[1] }}</b></p>
                      <p><b>Events</b>: {{ filterConf.competition_type }}</p>
                      <p><b>Läufe</b>: {{ filterConf.race_phase_type }}</p>
                      <p><b>Läufe (erweitert)</b>: {{ filterConf.race_phase_subtype }}</p>
                      <p><b>Platzierung</b>: {{ filterConf.placement ? filterConf.placement : 'alle' }}</p>
                    </v-col>
                  </v-row>
                </v-alert>
                <v-table class="tableStyles" density="compact" v-if="tableData.results > 0">
                  <tbody class="nth-grey">
                    <tr>
                      <th>Weltbestzeit</th>
                      <td>{{
                        tableData.world_best_time_boat_class ?
                        `${formatMilliseconds(tableData.world_best_time_boat_class)}` : "–"
                        }}
                      </td>
                    </tr>
                    <tr>
                      <th>Beste im Zeitraum</th>
                      <td>{{ formatMilliseconds(tableData.best_in_period) }}</td>
                    </tr>
                    <tr>
                      <th>Ø Geschwindigkeit (m/s)</th>
                      <td>{{ tableData["mean"]["m/s"] }}</td>
                    </tr>
                    <tr>
                      <th>Ø t über 500m</th>
                      <td>{{ formatMilliseconds(tableData["mean"]["pace 500m"]) }}</td>
                    </tr>
                    <tr>
                      <th>Ø t über 1000m</th>
                      <td>{{ formatMilliseconds(tableData["mean"]["pace 1000m"]) }}</td>
                    </tr>
                    <tr>
                      <th>Ø t über 2000m</th>
                      <td>{{ formatMilliseconds(tableData["mean"]["mm:ss,00"]) }}</td>
                    </tr>
                    <tr>
                      <th>Standardabweichung</th>
                      <td>{{ formatMilliseconds(tableData.std_dev) }}</td>
                    </tr>
                    <tr>
                      <th>Median</th>
                      <td>{{ formatMilliseconds(tableData.median) }}</td>
                    </tr>
                    <tr>
                      <th></th>
                      <td style="font-style: italic;">Bedingungen</td>
                    </tr>
                    <tr>
                      <th>Abstufung schnellste</th>
                      <td>(n={{ tableData["gradation_fastest"]["results"] }})
                        {{ formatMilliseconds(tableData["gradation_fastest"]["time"]) }}
                      </td>
                    </tr>
                    <tr>
                      <th>Abstufung mittel</th>
                      <td>(n={{ tableData["gradation_medium"]["results"] }}) {{
                        formatMilliseconds(tableData["gradation_medium"]["time"])
                        }}
                      </td>
                    </tr>
                    <tr>
                      <th>Abstufung langsam</th>
                      <td>(n={{ tableData["gradation_slow"]["results"] }}) {{
                        formatMilliseconds(tableData["gradation_slow"]["time"])
                        }}
                      </td>
                    </tr>
                    <tr>
                      <th>Abstufung langsamste</th>
                      <td>(n={{ tableData["gradation_slowest"]["results"] }})
                        {{ formatMilliseconds(tableData["gradation_slowest"]["time"]) }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-col>

              <v-col :cols="mobile ? 12 : 7" class="pa-0" v-if="tableData.results > 0">
                <v-container style="width: 100%" class="pa-2">
                  <BarChart :height="'100%'" :width="'100%'" :data="getBarChartData" :chartOptions="barChartOptions"
                    class="chart-bg">
                  </BarChart>
                </v-container>
                <v-container style="width: 100%" class="pa-2">
                  <ScatterChart :height="'100%'" :width="'100%'" :data="getScatterChartData"
                    :chartOptions="scatterChartOptions" class="chart-bg"></ScatterChart>
                </v-container>
              </v-col>

            </v-row>

            <!-- Multiple Boat Classes -->
            <v-row v-if="currentView == 'Alle'">
              <v-col :cols="mobile ? 12 : 8" class="py-0 pt-1">
                <v-alert type="success" variant="tonal" class="my-2">
                  <p><b>{{matrixResults}} Datensätze |
                      Von {{ filterConf.interval[0] }} bis {{ filterConf.interval[1] }}</b></p>
                  <p><b>Events</b>: {{ filterConf.competition_type }}</p>
                  <p><b>Läufe</b>: {{ filterConf.race_phase_type }}</p>
                  <p><b>Läufe (erweitert)</b>: {{ filterConf.race_phase_subtype }}</p>
                  <p><b>Platzierung</b>: {{ filterConf.placement ? filterConf.placement : 'alle' }}</p>
                </v-alert>
              </v-col>

              <v-col :cols="mobile ? 12 : 8" class="py-0">
                <v-table class="tableStyles" density="compact">
                  <thead>
                    <tr>
                      <th></th>
                      <th>WBT [min]</th>
                      <th>Ø Zeit [min]</th>
                      <th>SD [min]</th>
                      <th>n</th>
                    </tr>
                  </thead>
                  <tbody class="nth-grey">
                    <template v-for="row in matrixTableData">
                      <tr v-if="(typeof row === 'string')" class="subheader">
                        <th><b>{{ row }}</b></th>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                      </tr>
                      <tr v-else>
                        <td v-for="item in row">
                          {{ item }}
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </v-table>
              </v-col>

            </v-row>


            <!-- Matrix-->
            <div v-if="currentView=='Matrix'">
              <h2 class="pb-2">{{matrixCompetitions.join(", ")}}</h2>
            
            <v-table class="tableStyles" density="compact">
              <thead>
                <tr>
                  <th v-for="header in getMatrixTable[0]" :key="header">{{ header }}</th>
                </tr>
              </thead>
              <tbody class="nth-grey">
                <template v-for="row in getMatrixTable.slice(1)">
                  <tr>
                    <td v-for="item in row">
                      {{ item }}
                    </td>
                  </tr>
                </template>
              </tbody>
            </v-table>
            </div>
            

          </div>
        </v-container>
      </v-container>
    </v-layout>
  </v-card>
</template>

<script>
import { mapState } from "pinia";
import { useBerichteState } from "@/stores/berichteStore";
import { useGlobalState } from "@/stores/globalStore";

export default {
  computed: {
  ...mapState(useGlobalState, {
    headerReduced: "getHeaderReducedState"
  }),
  ...mapState(useBerichteState, {
    tableData: "getTableData",
    matrixResults: "getMatrixTableResults",
    matrixCompetitions: "getMatrixCompetitions",
    matrixTableData: "getMultipleTableData",
    getMatrixTable: "getMatrixTable",
    getBarChartData: "getBarChartData",
    barChartOptions: "getBarChartOptions",
    filterConf: "getFilterConfig",
    getScatterChartData: "getScatterChartData",
    scatterChartOptions: "getScatterChartOptions",
    filterState: "getFilterState",
    currentView: "getSelectedBoatClass",
    loading: "getLoadingState"
  })
},
  methods: {
    openPrintDialog() {
      window.print();
    },
    exportMatrixTableData() {
      const store = useBerichteState()
      store.exportMatrixTableData()
    },
    exportBoatClassTableData() {
      const store = useBerichteState()
      store.exportBoatClassTableData()
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useBerichteState()
      store.setFilterState(this.filterState)
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
    },
    formatMilliseconds(ms) {
      if (ms) {
        return new Date(ms).toISOString().slice(14, -2)
      } else {
        return 0
      }
    },
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
    let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
    document.documentElement.style.setProperty('--navbar-height', navbarHeight);
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
        const store = useBerichteState()
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

/*
.no-border {
  border-left: none !important;
  border-right: none !important;
}
*/

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

  i,
  .filterToggleButton,
  .filterToggleButtonMobile {
    display: none;
  }
}
</style>

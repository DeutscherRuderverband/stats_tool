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
          v-bind:style='{"margin-top" : (mobile? "71.25px" : "158px" )}'
          width="500">
        <rennstruktur-filter/>
      </v-navigation-drawer>
      <v-container :class="mobile ? 'pa-5 main-container' : 'px-10 pt-0 main-container'">
        <v-col cols="6" class="d-flex flex-row px-0" style="align-items: center">
          <h1>Rennstrukturanalyse</h1>
          <v-icon id="tooltip-analyis-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline
          </v-icon>
          <v-tooltip
              activator="#tooltip-analyis-icon"
              location="end"
              open-on-hover
          >Die Rennstrukturanalyse erlaubt die gezielte Betrachtung des Rennverlaufs auf Basis von Ergebnis- und GPS
            Daten.
          </v-tooltip>
          <a :href="emailLink" v-show="showEmailIcon">
            <v-icon color="grey" class="ml-2 v-icon--size-large">mdi-email-outline
            </v-icon>
          </a>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large"
                  v-if="displayRaceDataAnalysis">mdi-table-arrow-right
          </v-icon>
        </v-col>
        <v-divider></v-divider>
        <v-breadcrumbs style="color: grey; height: 22px" class="pa-0 my-2" :items="breadCrumbs"></v-breadcrumbs>
        <v-container class="pa-0" v-if="!displayRaceDataAnalysis">
          <v-row>
            <v-col cols="12">
              <h2>Suchergebnisse</h2>
              <v-container class="pa-0 mt-3">
                <v-col cols="12" class="pa-0">
                  <v-alert type="info" variant="tonal" v-if="!getAnalysis && !loading" :width="mobile ? '100%':'50%'">
                    Bitte wählen Sie ein Jahr und eine Wettkampfklasse in dem Filter auf der linken Seite.
                  </v-alert>
                  <v-progress-circular v-if="loading" indeterminate color="blue" size="40"></v-progress-circular>

                  <v-col :cols="mobile ? 12 : 6" class="pa-0">
                    <v-alert type="error" variant="tonal" class="my-2" v-if="getAnalysis && !getAnalysis.length > 0">
                      <v-row>
                        <v-col cols="12">
                          <p>Leider keine Ergebnisse gefunden.</p>
                        </v-col>
                      </v-row>
                    </v-alert>
                    <v-alert type="info" variant="tonal" class="my-2" v-if="noFurtherEntries">
                      <v-row>
                        <v-col cols="12">
                          <p>Hierzu liegen leider keine weiteren Einträge vor.</p>
                        </v-col>
                      </v-row>
                    </v-alert>
                  </v-col>

                  <!-- competition list -->
                  <v-list density="compact" v-show="displayCompetitions && !loading">
                    <div
                        :style="{'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem'}">
                      <v-list-item
                          min-height="80"
                          style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                          class="pa-2 mx-1"
                          v-for="competition in getAnalysis"
                          :key="competition"
                          :title="competition.name"
                          :subtitle="competition.start+' | '+competition.venue"
                          @click="getEvents(competition.events, competition.name, competition.id)"
                      ></v-list-item>
                    </div>
                  </v-list>

                  <!-- events list -->
                  <v-list density="compact" v-show="displayEvents && !loading">
                    <div
                        :style="{'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem'}">
                      <v-list-item
                          min-height="50"
                          style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                          class="pa-1 mx-1"
                          v-for="event in events"
                          :key="event"
                          :title="event.name"
                          @click="getRaces(event.races, event.name, event.id)"
                      ></v-list-item>
                    </div>
                  </v-list>


                  <!-- races list -->
                  <v-list density="compact" v-show="displayRaces && !loading">
                    <div
                        :style="{'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem'}">
                      <v-list-item
                          min-height="50"
                          style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                          class="pa-2 mx-1"
                          v-for="race in races"
                          :key="race"
                          :title="race.name"
                          @click="loadRaceAnalysis(race.name, race.id)"
                      ></v-list-item>
                    </div>
                  </v-list>
                </v-col>
              </v-container>
            </v-col>
          </v-row>
        </v-container>

        <v-container v-if="displayRaceDataAnalysis && !loading" class="px-0 py-2">

          <v-row no-gutters>
            <v-col cols="6">
              <h2>{{ `${competitionData.display_name} (${competitionData.boat_class})` }}</h2>
            </v-col>
            <v-col cols="6" class="text-right">
              <p style="color: grey">Bestzeiten: {{ formatMilliseconds(competitionData.result_time_world_best) }} (WB) |
                {{ formatMilliseconds(competitionData.result_time_best_of_current_olympia_cycle) }} (OZ/Jahr)</p>
              <p><b>{{ competitionData.venue }} | {{ competitionData.start_date }}</b></p>
            </v-col>
          </v-row>

          <v-container class="pa-0 d-flex">
            <v-col cols="6" class="pa-0">
            </v-col>
            <v-col cols="6" class="pa-0 text-right">
            </v-col>
          </v-container>

          <v-row>
            <v-col cols="12">
              <v-table class="tableStyles" density="compact">
                <thead>
                <tr>
                  <th v-for="tableHead in tableData[0]" class="px-2">{{ tableHead }}</th>
                </tr>
                </thead>
                <tbody class="nth-grey">
                <tr v-for="(country, idx) in tableData.slice(1)">
                  <td v-for="item in country" class="px-2">
                    <template v-if="Array.isArray(item)">
                      <p v-for="element in item">
                        {{ element }}
                      </p>
                    </template>
                    <template v-else>
                      <p>
                        {{ item }}
                      </p>
                    </template>
                  </td>
                </tr>
                </tbody>
              </v-table>
              <v-col class="text-right font-weight-black" style="font-size: 0.9em">
                <a v-if="competitionData.pdf_urls.result"
                   :href=competitionData.pdf_urls.result target="_blank" class="mr-2" style="color: black">
                  Ergebnisse
                  <v-icon color="grey">mdi-open-in-new</v-icon>
                </a>
                <a v-if="competitionData.pdf_urls.race_data"
                   :href=competitionData.pdf_urls.race_data target="_blank" class="ml-2" style="color: black">
                  GPS-Daten
                  <v-icon color="grey">mdi-open-in-new</v-icon>
                </a>
              </v-col>
            </v-col>
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container v-for="(data, idx) in getGPsData" :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="data" :chartOptions="gpsChartOptions[idx]" class="chart-bg"></LineChart>
              </v-container>
            </v-col>
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container v-for="(data, idx) in getIntermediateData" :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="data" :chartOptions="intermediateChartOptions[idx]" class="chart-bg"></LineChart>
              </v-container>
            </v-col>
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="deficitMeters" :chartOptions="deficitChartOptions" class="chart-bg"></LineChart>
              </v-container>
            </v-col>
          </v-row>
        </v-container>
      </v-container>
    </v-layout>
  </v-card>
</template>

<script setup>
import RennstrukturFilter from "@/components/filters/rennstrukturFilter.vue";
import LineChart from "@/components/charts/LineChart.vue";
import '@/assets/base.css';
import 'chartjs-adapter-moment';
import {Chart as ChartJS, Tooltip, Legend, TimeScale} from "chart.js";

ChartJS.register(Tooltip, Legend, TimeScale);
</script>

<script>
import {useRennstrukturAnalyseState} from "@/stores/baseStore";
import {mapState} from "pinia";
import router from "@/router";
import {useMedaillenspiegelState} from "@/stores/medaillenspiegelStore";

export default {
  computed: {
    ...mapState(useRennstrukturAnalyseState, {
      getAnalysis: "getAnalysisData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      competitionData: 'getCompetitionData'
    }),
    ...mapState(useRennstrukturAnalyseState, {
      oldTableData: "getOldTableData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      tableData: "getTableData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getGPsData: "getGPSChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getIntermediateData: "getIntermediateChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      filterState: "getFilterState"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      loading: "getLoadingState"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      deficitMeters: "getDeficitInMeters"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      intermediateChartOptions: "getIntermediateChartOptions"
    }),
  },
  data() {
    return {
      noFurtherEntries: false,
      filterOpen: false,
      breadCrumbs: [],
      mobile: false,
      showEmailIcon: false,
      emailLink: '',
      showTooltip: false,
      displayRaceDataAnalysis: false,
      displayCompetitions: true,
      displayEvents: false,
      displayRaces: false,
      events: {},
      races: {},
      lastCompId: null,
      lastEventId: null,
      gpsChartOptions: [{
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Strecke [m]'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Geschwindigkeit [m/sek]'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: "Geschwindigkeit"
          }
        }
      },
        {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Strecke [m]'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Schlagfrequenz [1/min]'
              }
            }
          },
          plugins: {
            title: {
              display: true,
              text: "Schlagfrequenz"
            }
          }
        }, {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Strecke [m]'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Vortrieb [m/Schlag]'
              }
            }
          },
          plugins: {
            title: {
              display: true,
              text: "Vortrieb"
            }
          }
        }
      ],
      deficitChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Strecke [m]'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Rückstand [m]'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: "Rückstand zum Führenden [m]"
          }
        }
      },
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
    this.filterOpen = this.filterState

    // possible solution for permanent url --> in the real scenario there must be a fetch to the backend
    window.onload = () => {
      const url = new URL(window.location.href);
      const race_id = url.searchParams.get("race_id");
      this.displayRaceDataAnalysis = !!race_id;
      if (race_id) {
        const store = useRennstrukturAnalyseState()
        store.fetchRaceData(race_id)
      }
    }
  },
  methods: {
    formatMilliseconds(ms) {
      if (!ms) {
        return '00:00.000';
      }
      return new Date(ms).toISOString().slice(14, -2);
    },
    openPrintDialog() {
      window.print();
    },
    exportTableData() {
      const store = useRennstrukturAnalyseState()
      store.exportTableData()
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useRennstrukturAnalyseState()
      store.setFilterState(this.filterState)
    },
    getEvents(competition, displayName, compId) {
      if (competition.length === 0) {
        this.noFurtherEntries = true
      }
      router.push("/rennstrukturanalyse/" + compId)
      this.lastCompId = compId
      this.events = competition
      this.breadCrumbs.push({title: displayName})
      this.displayCompetitions = false
      this.displayEvents = true
    },
    getRaces(events, displayName, eventId) {
      if (events.length === 0) {
        this.noFurtherEntries = true
      }
      router.push(this.$route.fullPath + "/" + eventId)
      this.lastEventId = eventId
      this.races = events
      this.breadCrumbs.push({title: displayName})
      this.displayEvents = false
      this.displayRaces = true
    },
    loadRaceAnalysis(raceName, raceId) {
      const store = useRennstrukturAnalyseState()
      store.fetchRaceData(raceId)
      this.showEmailIcon = true
      const newPath = `/rennstrukturanalyse/${this.lastCompId}/${this.lastEventId}?race_id=${raceId}`
      router.push(newPath)
      this.displayRaceDataAnalysis = true
      const subject = "Wettkampfergebnisse"
      const body = `Sieh dir diese Wettkampfergebnisse an: http://${window.location.host + newPath}`
      this.emailLink = `mailto:?subject=${subject}&body=${body}`
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth <= 750
      let navbarHeight = window.innerWidth < 750 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  watch: {
    filterState(newValue) {
      this.filterOpen = newValue;
    },
    filterOpen: function (newVal, oldVal) {
      if (oldVal === true && newVal === false && this.filterState === true) {
        const store = useRennstrukturAnalyseState()
        store.setFilterState(oldVal)
      }
    },
    loading() {
      router.push('/rennstrukturanalyse')
      this.displayRaceDataAnalysis = false
    },
    $route: {
      immediate: true,
      deep: true,
      handler(to, from) {
        if (typeof from !== 'undefined' && typeof to !== 'undefined') {
          // from events backwards to comp
          if (to.path === "/rennstrukturanalyse" && from.path.match(/\/rennstrukturanalyse\/[\w-]+/)) {
            this.noFurtherEntries = false
            this.displayEvents = false
            this.displayCompetitions = true
            this.displayRaces = false
            this.breadCrumbs.splice(0)
          }
          // from races backwards to events
          else if (from.path.match(/\/rennstrukturanalyse\/[\w-]+\/[\w-]+/) && !to.fullPath.includes("?race_id=")
              && !from.fullPath.includes("?race_id=") && to.path.match(/\/rennstrukturanalyse\/[\w-]+/)) {
            this.noFurtherEntries = false
            this.displayRaces = false
            this.displayCompetitions = false
            this.displayEvents = true
            this.breadCrumbs.splice(1)
          }
          // from comp forward to events
          else if (from.path === "/rennstrukturanalyse" && to.path.match(/\/rennstrukturanalyse\/[\w-]+/)) {
            this.displayRaces = false
            this.displayCompetitions = false
            this.displayEvents = true
            // only push to breadCrumbs if not yet done
            if (this.breadCrumbs.length === 0) {
              this.breadCrumbs.push({
                title: this.getAnalysis.find(obj => obj.id === this.lastCompId).display_name,
              })
            }
          } // from event forward to races
          else if (from.path.match(/\/rennstrukturanalyse\/[\w-]+/) && to.path.match(/\/rennstrukturanalyse\/[\w-]+\/[\w-]+/)
              && !to.fullPath.includes("?race_id=") && !from.fullPath.includes("?race_id=")) {
            this.displayRaces = true
            this.displayCompetitions = false
            this.displayEvents = false
            if (this.breadCrumbs.length === 1) {
              this.breadCrumbs.push({
                title: this.events.find(obj => obj.id === this.lastEventId).display_name,
              })
            }
          } else if (from.fullPath.includes("?race_id=") && !to.fullPath.includes("?race_id=") &&
              to.path.match(/\/rennstrukturanalyse\/[\w-]+\/[\w-]+/)) {
            this.displayRaceDataAnalysis = false
            this.displayEvents = false
            this.displayRaces = true
            this.showEmailIcon = false
            router.replace({path: `/rennstrukturanalyse/${this.lastCompId}/${this.lastEventId}`, query: {}})
          } else if (to.fullPath.includes("?race_id=")) {
            this.displayRaces = false
            this.displayRaceDataAnalysis = true
          }
        }
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

.nth-grey tr:nth-of-type(odd) {
  background-color: #f8f8f8;
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
  min-height: calc(100vh - (var(--navbar-height)) - 95px);
}

@media print {
  i, .filterToggleButton, .filterToggleButtonMobile {
    display: none;
  }
}
</style>

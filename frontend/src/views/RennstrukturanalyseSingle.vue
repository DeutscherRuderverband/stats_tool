<template>
  <v-container class="pa-0">

    <v-breadcrumbs style="color: grey; height: 22px" class="pa-0 my-2" :items="breadCrumbs"></v-breadcrumbs>

    <!--LOADING-->
    <div v-if="loading">
      <v-progress-circular class="pa-0 mt-3" indeterminate color="blue" size="40"></v-progress-circular>
    </div>

    <div v-else-if="!loading">
      <!-- Competitions  -->
      <div v-if="currentView === 'COMPETITIONS'">
        <h2>Suchergebnisse</h2>
        <v-container class="pa-0 mt-3">
          <v-col cols="12" class="pa-0">

            <v-container v-if="!getAnalysis" class="pa-0 mt-3">
              <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
                Bitte wähle ein Jahr und ein Event in dem Filter auf der linken Seite.
              </v-alert>
            </v-container>

            <v-container v-else-if="getAnalysis.length === 0" class="pa-0 mt-3">
              <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
                Leider keine Ergebnisse gefunden.
              </v-alert>
            </v-container>

            <v-list v-else density="compact">
              <div
                :style="{ 'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem' }">
                <v-list-item min-height="80"
                  style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                  class="pa-2 mx-1" v-for="competition in getAnalysis" :key="competition" :title="competition.name"
                  :subtitle="competition.start + ' | ' + competition.venue"
                  @click="getEvents(competition.events, competition.name, competition.id)"></v-list-item>
              </div>
            </v-list>

          </v-col>
        </v-container>
      </div>

      <!-- events list -->
      <div v-else-if="currentView === 'EVENTS'">
        <h2>Suchergebnisse</h2>
        <v-container class="pa-0 mt-3">
          <v-col cols="12" class="pa-0">

            <v-container v-show="events.length === 0" class="pa-0 mt-3">
              <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
                Hierzu liegen leider keine weiteren Einträge vor.
              </v-alert>
            </v-container>

            <v-list density="compact">
              <div
                :style="{ 'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem' }">
                <v-list-item min-height="50"
                  style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                  class="pa-1 mx-1" v-for="event in events" :key="event" :title="event.name"
                  @click="getRaces(event.races, event.name, event.id)"></v-list-item>
              </div>
            </v-list>

          </v-col>
        </v-container>
      </div>

      <!-- Races  -->
      <div v-else-if="currentView === 'RACES'">
        <h2>Suchergebnisse</h2>
        <v-container class="pa-0 mt-3">
          <v-col cols="12" class="pa-0">

            <v-container v-if="races.length === 0" class="pa-0 mt-3">
              <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
                Hierzu liegen leider keine weiteren Einträge vor.
              </v-alert>
            </v-container>

            <v-list density="compact">
              <div
                :style="{ 'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem' }">
                <v-list-item min-height="50"
                  style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                  class="pa-2 mx-1" v-for="race in races" :key="race" :title="race.name"
                  @click="loadRaceAnalysis(race.name, race.id)"></v-list-item>
              </div>
            </v-list>

          </v-col>
        </v-container>
      </div>

      <!-- Single Rennstrukturanalyse -->
      <div v-else-if="currentView === 'ANALYSIS'">
        <v-container class="px-0 py-2">
          <v-row no-gutters>
            <v-col cols="6" class="pt-3">
              <h2>{{ `${competitionData.display_name} (${competitionData.boat_class})` }}</h2>
            </v-col>

            <v-spacer></v-spacer>

            <v-col cols="auto" class="align-center pt-2" style="color: grey">
              Bestzeiten:
              <v-tooltip activator="parent" location="bottom">
                Berechnung der Relationszeit zu ausgewählter Bestzeit
              </v-tooltip>
            </v-col>

            <v-col cols="auto" class="pt-0 pl-0 pb-1 text-right">
              <v-radio-group v-model="radios" dense inline class="mb-n7 pb-0">
                <v-radio color="blue" :label="`${formatMilliseconds(competitionData.result_time_world_best)} (WBT)`"
                  value="wbt"></v-radio>
                <v-radio color="blue"
                  :label="`${formatMilliseconds(competitionData.result_time_world_best_before_olympia_cycle)} (WBT vor OZ)`"
                  value="ozt"></v-radio>
              </v-radio-group>
              <p class="pt-0 mt-0"><b>{{ competitionData.venue }} | {{ competitionData.start_date }}</b></p>
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
              <p v-show="outliers.size > 0" style="color: orange">
                <v-icon color="orange">mdi-information</v-icon>
                <b>Diese Tabelle enthält Ausreißerwerte.</b>
              </p>
              <v-table class="tableStyles" density="compact">
                <thead>
                  <tr>
                    <th v-for="tableHead in tableData[0]" class="px-2">
                      <p>{{ tableHead.text }}<v-tooltip activator="parent" location="bottom"
                          v-if="tableHead.tooltip != null">{{ tableHead.tooltip }}</v-tooltip></p>
                    </th>
                  </tr>
                </thead>
                <tbody class="nth-grey">
                  <tr v-for="(country, idx) in tableData.slice(1)">
                    <td v-for="item in country" :key="item" class="px-2"
                      :style="{ color: Array.from(outliers).includes(idx) ? 'orange' : '' }">
                      <template v-if="Array.isArray(item)">
                        <template v-for="element in item">
                          <a v-if="element && typeof element === 'object'
                            && element.hasOwnProperty('link') && element.hasOwnProperty('name')" :href="element.link"
                            class="link-underline">
                            {{ element.name }}<br />
                          </a>
                          <p v-else-if="element">{{ element }}</p>
                        </template>
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
              <v-col class="d-flex align-center justify-space-between font-weight-black px-0" style="font-size: 0.9em">
                <p class="mr-2"><b>Progression:</b> {{ competitionData.progression_code || '–' }}</p>
                <div class="text-right">
                  <a v-if="competitionData.pdf_urls.result" :href=competitionData.pdf_urls.result target="_blank"
                    class="mr-2" style="color: black">
                    Ergebnisse
                    <v-icon color="grey">mdi-open-in-new</v-icon>
                  </a>
                  <a v-if="competitionData.pdf_urls.race_data" :href=competitionData.pdf_urls.race_data target="_blank"
                    class="ml-2" style="color: black">
                    GPS-Daten
                    <v-icon color="grey">mdi-open-in-new</v-icon>
                  </a>
                </div>
              </v-col>
            </v-col>
          </v-row>

          <v-row>
            <h3 class="pl-4">Visualisierungsoptionen</h3>
          </v-row>
          <v-row>
            <v-col>
              <v-select label="Zeige Differenz zu" class="pt-0" compact :items="getChartOptions.boats"
                v-model="getChartOptions.difference_to" variant="outlined">
              </v-select>
            </v-col>
            <v-col>
              <v-select label="Boote in Visualisierungen" class="pt-0" compact multiple :items="getChartOptions.boats"
                v-model="getChartOptions.boats_in_chart" variant="outlined">
              </v-select>
            </v-col>
          </v-row>

          <v-row class="pt-0 mt-0">
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getGPsData[0]" :chartOptions="chartMetadata[0]" class="chart-bg">
                </LineChart>
              </v-container>
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getGPsData[2]" :chartOptions="chartMetadata[1]" class="chart-bg">
                </LineChart>
              </v-container>
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getIntermediateData[1]" :chartOptions="chartMetadata[2]" class="chart-bg">
                </LineChart>
              </v-container>
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getIntermediateData[2]" :chartOptions="chartMetadata[6]" class="chart-bg">
                </LineChart>
              </v-container>
            </v-col>
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getGPsData[1]" :chartOptions="chartMetadata[3]" class="chart-bg">
                </LineChart>
              </v-container>
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getIntermediateData[0]" :chartOptions="chartMetadata[4]" class="chart-bg">
                </LineChart>
              </v-container>
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="deficitMeters" :chartOptions="chartMetadata[5]" class="chart-bg">
                </LineChart>
              </v-container>
            </v-col>
          </v-row>

        </v-container>
      </div>

    </div>


  </v-container>
</template>

<script setup>
import LineChart from "@/components/charts/LineChart.vue";
import '@/assets/base.css';
import 'chartjs-adapter-moment';
import { Chart as ChartJS, Tooltip, Legend, TimeScale } from "chart.js";

ChartJS.register(Tooltip, Legend, TimeScale);
</script>

<script>
import { useRennstrukturAnalyseState } from "@/stores/baseStore";
import { mapState } from "pinia";
import router from "@/router";

export default {
  computed: { 
    ...mapState(useRennstrukturAnalyseState, {
      loading: "getLoadingState",
      wbt: "getRelationTimeFrom",
      outliers: "getOutlierCountries",
      getAnalysis: "getAnalysisData",
      competitionData: "getCompetitionData",

      // Table data
      tableData: "getTableData",

      // Chart data
      getGPsData: "getGPSChartData",
      getIntermediateData: "getIntermediateChartData",
      deficitMeters: "getDeficitInMeters",

      // Global chart options
      getChartOptions: "getSingleOptions",

      // Chart options for graphs
      chartMetadata: "getChartMetadata",
    }),

    currentView() {
      if (this.$route.query.race_id) {
        return "ANALYSIS"
        // Bread crumbs length 3
      }
      if (this.$route.path.match(/\/single\/[^/]+\/[^/]+/)) {
        //Bread crumbs length 2
        return "RACES"
      }
      if (this.$route.path.match(/\/single\/[^/]+/)) {
        // Bread crumb length 1
        return "EVENTS"
      }
      return "COMPETITIONS"
    }
  },

  data() {
    return {
      breadCrumbs: [],
      mobile: false,
      events: [],
      races: [],
      radios: "wbt",
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();

    this.radios = this.wbt;

    const store = useRennstrukturAnalyseState();

    // Handle ?competition_id
    const comp_id = this.$route.query.competition_id;
    if (comp_id) {
      console.log("Lade Wettkampf (initial):", comp_id);
      store.fetchCompetitionData({ competition_id: comp_id });
      store.setDisplay("SINGLE");
    }

    // Handle ?race_id
    const race_id = this.$route.query.race_id;
    if (race_id) {
      console.log("Lade Rennen (initial):", race_id);
      store.fetchRaceData(race_id);
    }
  },
  methods: {
    formatMilliseconds(ms) {
      if (!ms) {
        return '00:00.00';
      }
      return new Date(ms).toISOString().slice(14, -2);
    },
    getEvents(competition, displayName, compId) {
      router.push("/rennstrukturanalyse/single/" + compId)
      competition.sort((a, b) => a.boat_class.localeCompare(b.boat_class))
      this.events = competition
      this.breadCrumbs.push({ title: displayName })
    },
    getRaces(events, displayName, eventId) {
      router.push(this.$route.fullPath + "/" + eventId)
      this.races = events
      this.breadCrumbs.push({ title: displayName })
    },
    async loadRaceAnalysis(raceName, raceId) {
      const store = useRennstrukturAnalyseState()
      store.setToLoadingState(true)
      const newPath = this.$route.fullPath + `?race_id=${raceId}`
      router.push(newPath)
      await store.fetchRaceData(raceId)
      const subject = "Wettkampfergebnisse"
      const body = `Sieh dir diese Wettkampfergebnisse an: http://${window.location.host + newPath}`
      store.setEmailLink(`mailto:?subject=${subject}&body=${body}`)
      store.setToLoadingState(false)
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    },
    setRelationTimeFrom(value) {
      const store = useRennstrukturAnalyseState()
      store.setRelationTimeFrom(value)
    }
  },
  watch: {
    radios(newValue) {
      const store = useRennstrukturAnalyseState()
      store.setRelationTimeFrom(newValue)
    },
    $route: {
      immediate: true,
      deep: true,
      async handler(to) {
        if (!to) return;

        const store = useRennstrukturAnalyseState()
        const raceId = to.query.race_id;
        const compId = to.params.comp_id;
        const eventId = to.params.event_id;

        const addBreadCrumbs = (comp, event = null) => {
          const crumbs = [];

          if (comp) {
            crumbs.push({ title: comp.name });
          }

          if (event) {
            crumbs.push({ title: event.name });
          }

          const current = this.breadCrumbs.map(c => c.title);
          const desired = crumbs.map(c => c.title);

          const isEqual =
            current.length === desired.length &&
            current.every((title, i) => title === desired[i]);

          if (!isEqual) {
            this.breadCrumbs.splice(0, this.breadCrumbs.length, ...crumbs);
          }
        };


        //single
        if (!compId) {
          this.breadCrumbs.splice(0);
        }

        //single/comp
        if (compId && !eventId) {

          let comp = (this.getAnalysis ?? []).find(obj => obj.id == compId);

          if (comp) {
            addBreadCrumbs(comp, null)
            if (this.events.length === 0) {
              this.events = comp.events
            }
          }
          else {
            try {
              const data = { competition_id: compId };
              await store.fetchCompetitionData(data);
              comp = (this.getAnalysis ?? []).find(obj => obj.id == compId);
              this.events = comp?.events ?? [];
              addBreadCrumbs(comp, null);
            } catch (error) {
              console.error("Failed to fetch comp:", error);
            }
          }
        }

        //single/comp/event
        else if (eventId && compId) {

          let comp = (this.getAnalysis ?? []).find(obj => obj.id == compId);
          let event = (this.events ?? []).find(obj => obj.id == eventId);

          if (comp && event) {
            addBreadCrumbs(comp, event);
          } else {
            try {
              const data = { competition_id: compId };
              await store.fetchCompetitionData(data);
              comp = (this.getAnalysis ?? []).find(obj => obj.id == compId);
              this.events = comp?.events ?? [];
              event = (comp?.events ?? []).find(obj => obj.id == eventId);
              this.races = event?.races ?? [];
              addBreadCrumbs(comp, event)
            } catch (error) {
              console.error("Failed to fetch comp:", error);
            }
          }
        }

        //race
        if (raceId) {
          if (raceId == this.competitionData.raceId) return;
          else {
            store.setToLoadingState(true)
            await store.fetchRaceData(raceId);
            store.setToLoadingState(false)
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
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}

@media print {

  i,
  .filterToggleButton,
  .filterToggleButtonMobile,
  .sources {
    display: none;
  }
}

.link-underline {
  text-decoration: none;
  color: #1369b0;
}

.link-underline:hover {
  text-decoration: none;
  color: black;
  border-bottom: 1px solid black;
}

.padding {
  padding-top: 30px;
  /* Adds 20 pixels of padding at the bottom */
  color: white
}
</style>

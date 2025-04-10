<template>
  <!-- Filter Button-->
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
      <!-- Open Filter Menu-->
      <v-navigation-drawer v-model="filterOpen" temporary
        v-bind:style='{ "margin-top": (mobile ? "71.25px" : (headerReduced ? "81px" : "159px")) }' width="500">
        <rennstruktur-filter />
      </v-navigation-drawer>

      <!-- Main Content-->
      <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
        <!-- Heading "Rennstrukturanalyse" + icon options -->
        <v-col cols="6" class="d-flex flex-row px-0" style="align-items: center"
          v-bind:style='{ "padding-top": windowWidth < 400 ? "18px" : "12px" }, { "padding-bottom": (windowWidth < 400 ? "18px" : "12px") }'>
          <h1 v-bind:style='{ "font-size": (windowWidth < 400 ? "22px" : "30px") }'>Rennstrukturanalyse</h1>
          <v-icon id="tooltip-analysis-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline
          </v-icon>
          <v-tooltip activator="#tooltip-analysis-icon" location="end" open-on-hover>Die Rennstrukturanalyse erlaubt die Betrachtung des Rennverlaufes
            ein oder mehrerer Rennen basierend auf Ergebnis- und GPS-Daten.
          </v-tooltip>
          <a :href="emailLink" v-show="showEmailIcon">
            <v-icon color="grey" class="ml-2 v-icon--size-large">mdi-email-outline
            </v-icon>
          </a>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large"
            v-if="displayRaceDataAnalysis">mdi-table-arrow-right
          </v-icon>
          <v-icon @click="exportRaces()" color="grey" class="ml-2 v-icon--size-large"
            v-if="display == 'MULTIPLE'">mdi-table-arrow-right
          </v-icon>
        </v-col>
        <v-divider></v-divider>

        <!--LOADING-->
        <v-progress-circular v-if="loading" class="pa-0 mt-3" indeterminate color="blue"
          size="40"></v-progress-circular>

        <!--EMPTY-->
        <v-container class="pa-0 mt-3" v-if="display == 'EMPTY' && !loading">
          <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
            Bitte wähle ein Jahr und ein Event in dem Filter auf der linken Seite.
          </v-alert>
        </v-container>

        <!-- SINGLE -->
        <v-container v-if="display == 'SINGLE' && !loading" class="pa-0">
          <v-breadcrumbs v-if="getAnalysis" style="color: grey; height: 22px" class="pa-0 my-2"
            :items="breadCrumbs"></v-breadcrumbs>
          <!-- competition/ event/ races lists -->
          <v-container class="pa-0" v-if="!displayRaceDataAnalysis">
            <v-row>
              <v-col cols="12">
                <h2 v-if="getAnalysis">Suchergebnisse</h2>
                <v-container class="pa-0 mt-3">
                  <v-col cols="12" class="pa-0">
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
                    <v-list density="compact" v-show="displayCompetitions">
                      <div
                        :style="{ 'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem' }">
                        <v-list-item min-height="80"
                          style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                          class="pa-2 mx-1" v-for="competition in getAnalysis" :key="competition"
                          :title="competition.name" :subtitle="competition.start + ' | ' + competition.venue"
                          @click="getEvents(competition.events, competition.name, competition.id)"></v-list-item>
                      </div>
                    </v-list>

                    <!-- events list -->
                    <v-list density="compact" v-show="displayEvents">
                      <div
                        :style="{ 'display': 'grid', 'grid-template-columns': (mobile ? '1fr' : 'repeat(2, 1fr)'), 'grid-gap': '0.5rem' }">
                        <v-list-item min-height="50"
                          style="background-color: whitesmoke; border-radius: 5px; border-left: 8px solid #5cc5ed;"
                          class="pa-1 mx-1" v-for="event in events" :key="event" :title="event.name"
                          @click="getRaces(event.races, event.name, event.id)"></v-list-item>
                      </div>
                    </v-list>

                    <!-- races list -->
                    <v-list density="compact" v-show="displayRaces">
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
              </v-col>
            </v-row>
          </v-container>

          <!-- Single Rennstrukturanalyse -->
          <v-container v-if="displayRaceDataAnalysis" class="px-0 py-2">
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
                  <v-radio color="blue" :label="`${formatMilliseconds(competitionData.result_time_world_best)} (WBT)`" value="wbt"></v-radio>
                  <v-radio color="blue" :label="`${formatMilliseconds(competitionData.result_time_world_best_before_olympia_cycle)} (WBT vor OZ)`" value="ozt"></v-radio>
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
                <v-col class="d-flex align-center justify-space-between font-weight-black px-0"
                  style="font-size: 0.9em">
                  <p class="mr-2"><b>Progression:</b> {{ competitionData.progression_code || '–' }}</p>
                  <div class="text-right">
                    <a v-if="competitionData.pdf_urls.result" :href=competitionData.pdf_urls.result target="_blank"
                      class="mr-2" style="color: black">
                      Ergebnisse
                      <v-icon color="grey">mdi-open-in-new</v-icon>
                    </a>
                    <a v-if="competitionData.pdf_urls.race_data" :href=competitionData.pdf_urls.race_data
                      target="_blank" class="ml-2" style="color: black">
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
                  <LineChart :data="getGPsData[0]" :chartOptions="singleChartOptions[0]" class="chart-bg"></LineChart>
                </v-container>
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="getGPsData[2]" :chartOptions="singleChartOptions[1]" class="chart-bg"></LineChart>
                </v-container>
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="getIntermediateData[1]" :chartOptions="singleChartOptions[2]" class="chart-bg">
                  </LineChart>
                </v-container>
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="getIntermediateData[2]" :chartOptions="singleChartOptions[6]" class="chart-bg">
                  </LineChart>
                </v-container>
              </v-col>
              <v-col :cols="mobile ? 12 : 6" class="pa-0">
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="getGPsData[1]" :chartOptions="singleChartOptions[3]" class="chart-bg"></LineChart>
                </v-container>
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="getIntermediateData[0]" :chartOptions="singleChartOptions[4]" class="chart-bg">
                  </LineChart>
                </v-container>
                <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                  <LineChart :data="deficitMeters" :chartOptions="singleChartOptions[5]" class="chart-bg"></LineChart>
                </v-container>
              </v-col>
            </v-row>

          </v-container>
        </v-container>

        <!-- MULTIPLE -->
        <v-container v-if="display == 'MULTIPLE' && !loading" class="px-0 pt-4">

          <v-row>
            <v-col cols="6" class="pt-3 align-center">
              <h2>Vergleich Rennstruktur {{ boatClassData.boat_class }}</h2>
            </v-col>

            <v-spacer></v-spacer>

            <v-col cols="auto" class="align-center pt-5" style="color: grey">
              Bestzeiten:
              <v-tooltip activator="parent" location="bottom">
                Berechnung der Relationszeit zu ausgewählter Bestzeit
              </v-tooltip>
            </v-col>

            <v-col cols="auto" class="pb-0 pl-0 mb-n3">
              <v-radio-group v-model="wbt" dense inline>
                <v-radio color="blue" :label="`${boatClassData.wbt} (WBT)`" value="wbt" @click="setRelationTimeFrom('wbt')" :disabled="boatClassData.wbt == '00:00.00'"></v-radio>
                <v-radio color="blue" :label="`${boatClassData.wbt_oz} (WBT vor OZ)`" value="ozt" @click="setRelationTimeFrom('ozt')" :disabled="boatClassData.wbt_oz == '00:00.00'"></v-radio>
              </v-radio-group>
            </v-col>

          </v-row>

          <v-table class="tableStyles" density="compact">
            <thead>
              <tr>
                <th v-for="tableHead in multipleTableData[0]" class="px-2">
                  <p>{{ tableHead.text }}<v-tooltip activator="parent" location="bottom"
                      v-if="tableHead.tooltip != null">{{
                      tableHead.tooltip }}</v-tooltip></p>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(country, idx) in multipleTableData.slice(1)">
                <td v-for="item in country" :key="item" class="px-2"
                  :style="{ color: Array.from(outliers).includes(idx) ? 'orange' : '' }">
                  <template v-if="Array.isArray(item)">
                    <template v-for="element in item">
                      <p>{{ element }}</p>
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
          <p>Die Tabelle zeigt für jede Gruppe die durchschnittlichen Werte über alle Rennen</p>

          <v-row>
            <h3 class="pl-3 pt-10">Visualisierungsoptionen</h3>
          </v-row>
          <v-row>
            <v-col>
              <v-select label="95% Konfidenzintervall" class="pt-0" compact
                :items="getMultipleChartOptions.confidenceIntervalOptions"
                v-model="getMultipleChartOptions.showConfidenceInterval" variant="outlined">
              </v-select>
            </v-col>
            <v-col>
              <v-select label="Gruppen in Visualisierungen" class="pt-0" compact multiple
                :items="getMultipleChartOptions.groups" v-model="getMultipleChartOptions.groups_in_chart"
                variant="outlined">
              </v-select>
            </v-col>
          </v-row>

          <!-- Graphen -->
          <v-row class="mt-0 pt-0">
            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getMeanPacingProfiles" :chartOptions="multipleChartOptions[0]" class="chart-bg">
                </LineChart>
              </v-container>

              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getMeanGPsData[2]" :chartOptions="multipleChartOptions[1]" class="chart-bg">
                </LineChart>
              </v-container>

              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getMeanIntermediateData" :chartOptions="multipleChartOptions[2]" class="chart-bg">
                </LineChart>
              </v-container>
            </v-col>

            <v-col :cols="mobile ? 12 : 6" class="pa-0">
              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getMeanGPsData[0]" :chartOptions="multipleChartOptions[3]" class="chart-bg">
                </LineChart>
              </v-container>

              <v-container :class="mobile ? 'pa-0' : 'pa-2'">
                <LineChart :data="getMeanGPsData[1]" :chartOptions="multipleChartOptions[4]" class="chart-bg">
                </LineChart>
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
import { Chart as ChartJS, Tooltip, Legend, TimeScale } from "chart.js";

ChartJS.register(Tooltip, Legend, TimeScale);
</script>

<script>
import { useRennstrukturAnalyseState } from "@/stores/baseStore";
import { mapState } from "pinia";
import router from "@/router";
import { useGlobalState } from "@/stores/globalStore";

export default {
  computed: {
    ...mapState(useGlobalState, {
      headerReduced: "getHeaderReducedState"
    }),

    ...mapState(useRennstrukturAnalyseState, {
      loading: "getLoadingState"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      filterState: "getFilterState"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      display: "getDisplay"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      wbt: "getRelationTimeFrom"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      outliers: "getOutlierCountries" 
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getAnalysis: "getAnalysisData"
    }),
    ...mapState(useRennstrukturAnalyseState, {    //Used for general information about competition
      competitionData: 'getCompetitionData'
    }),
    ...mapState(useRennstrukturAnalyseState, { 
      boatClassData: "getBoatClassData"
    }),

    //Table data
    ...mapState(useRennstrukturAnalyseState, {
      multipleTableData: "getMultipleTableData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      tableData: "getTableData"
    }),

    //Chart data
    ...mapState(useRennstrukturAnalyseState, {
      getGPsData: "getGPSChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getMeanGPsData: "getMeanGPSChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getIntermediateData: "getIntermediateChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getMeanIntermediateData: "getMeanIntermediateChartData"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      deficitMeters: "getDeficitInMeters"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getMeanPacingProfiles: "getMeanPacingProfiles"
    }),
    //global chart options
    ...mapState(useRennstrukturAnalyseState, {
      getChartOptions: "getSingleOptions"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      getMultipleChartOptions: "getMultipleOptions"
    }),
    //chart options for graphs
    ...mapState(useRennstrukturAnalyseState, {
      singleChartOptions: "getSingleChartOptions"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      multipleChartOptions: "getMultipleChartOptions"
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
      radios: "wbt",
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
    this.filterOpen = this.filterState
    this.radios = this.wbt

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
        return '00:00.00';
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
    exportRaces() {
      const store = useRennstrukturAnalyseState()
      store.exportRaces()
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
      competition.sort((a, b) => a.boat_class.localeCompare(b.boat_class))
      this.events = competition
      this.breadCrumbs.push({ title: displayName })
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
      this.breadCrumbs.push({ title: displayName })
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
      this.mobile = this.windowWidth < 900
      let navbarHeight = window.innerWidth < 900 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    },
    setRelationTimeFrom(value) {
      const store = useRennstrukturAnalyseState()
      store.setRelationTimeFrom(value)
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
    radios(newValue) {
      const store = useRennstrukturAnalyseState()
      store.setRelationTimeFrom(newValue)
    },
    $route: {
      immediate: true,
      deep: true,
      handler(to, from) {

        if (typeof to !== 'undefined') {
          // redirect from calendar to RSA 
          if (to.fullPath.includes("?competition_id=")) {
            const url = new URL(window.location.href);
            const comp_id = url.searchParams.get("competition_id");
            this.displayCompetitions = !!comp_id;
            const store = useRennstrukturAnalyseState()
            const data = {
              "competition_id": comp_id
            }
            store.fetchCompetitionData(data)
            store.setDisplay('SINGLE')
          }
        }
        if (typeof from !== 'undefined' && typeof to !== 'undefined') {
          // from events backwards to comp
          if (to.path === "/rennstrukturanalyse" && from.path.match(/\/rennstrukturanalyse\/[\w-]+/)) {
            this.noFurtherEntries = false
            this.displayEvents = false
            this.displayCompetitions = true
            this.displayRaces = false
            this.breadCrumbs.splice(0)
            const store = useRennstrukturAnalyseState()
            store.setDisplay('SINGLE')
          }
          // from races backwards to events
          else if (from.path.match(/\/rennstrukturanalyse\/[\w-]+\/[\w-]+/) && !to.fullPath.includes("?race_id=")
            && !from.fullPath.includes("?race_id=") && to.path.match(/\/rennstrukturanalyse\/[\w-]+/)) {
            this.noFurtherEntries = false
            this.displayRaces = false
            this.displayCompetitions = false
            this.displayEvents = true
            this.breadCrumbs.splice(1)
            const store = useRennstrukturAnalyseState()
            store.setDisplay('SINGLE')
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
            const store = useRennstrukturAnalyseState()
            store.setDisplay('SINGLE')
          } else if (from.fullPath.includes("?race_id=") && !to.fullPath.includes("?race_id=") &&
            to.path.match(/\/rennstrukturanalyse\/[\w-]+\/[\w-]+/)) {
            this.displayRaceDataAnalysis = false
            this.displayEvents = false
            this.displayRaces = true
            this.showEmailIcon = false
            router.replace({ path: `/rennstrukturanalyse/${this.lastCompId}/${this.lastEventId}`, query: {} })
            const store = useRennstrukturAnalyseState()
            store.setDisplay('SINGLE')
          } else if (to.fullPath.includes("?race_id=")) {
            this.displayRaces = false
            this.displayRaceDataAnalysis = true
            const store = useRennstrukturAnalyseState()
            store.setDisplay('SINGLE')
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

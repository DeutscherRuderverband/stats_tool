<template>
  <v-btn color="blue"
         @click="setFilterState()" v-show="!filterOpen"
         :class="mobile ? 'filterToggleButtonMobile mt-6 pa-0 ma-0' : 'filterToggleButton mt-6 pa-0 ma-0'"
         :height="mobile ? 100: 180"
         size="x-small"
  >
  <p style="writing-mode: vertical-rl; font-size: 16px; transform: rotate(180deg);">
    <v-icon style="transform: rotate(180deg); font-size: 14px; padding-left: 6px; padding-top: 10px;">mdi-filter</v-icon>
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
        <athleten-filter/>
      </v-navigation-drawer>

      <v-container :class="mobile ? 'px-5 py-2 pb-8 main-container' : 'px-10 py-0 pb-8 main-container'">
        <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
          <h1>Athleten</h1>
          <v-icon id="tooltip-athlete-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline</v-icon>
          <v-tooltip
              activator="#tooltip-athlete-icon"
              location="end"
              open-on-hover
          >Hier können die Stammdaten sowie alle Wettkampfergebnisse eines Athleten eingesehen werden.
          </v-tooltip>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
        </v-col>
        <v-divider></v-divider>

        <v-col class="pa-0" :cols="mobile ? 12 : 6" v-if="!data.name">
        <v-container class="pa-0 mt-3">
                <v-col cols="12" class="pa-0">

                    <v-alert type="info" variant="tonal" >
                    <p>Bitte wähle einen Athleten im Filter auf der linken Seite.</p>
                      </v-alert>
          </v-col>
        </v-container>
        </v-col>

        <v-container class="pa-0 mt-3" v-else>
          <v-row>
            <v-col :cols="mobile ? 12 : 4">
              <h2>{{ data.name }}</h2>
              <v-table class="tableStyles" density="compact">
                <tbody class="nth-grey">
                <tr>
                  <th>Nation</th>
                  <td>{{data.nation ? `${data.nation}` : '–'}}</td>
                </tr>
                <tr>
                  <th>Geburtsdatum</th>
                  <td>{{data.dob ? `${data.dob}` : '–'}}</td>
                </tr>
                <tr>
                  <th>Geschlecht</th>
                  <td>{{data.gender ? (data.gender == "Men" ? "Männlich" : "Weiblich") : '–'}}</td>
                </tr>
                <tr>
                  <th>Gewicht</th>
                  <td>{{data.weight ? `${data.weight}kg` : "–"}}</td>
                </tr>
                <tr>
                  <th>Größe</th>
                  <td>{{data.height ? `${data.height}cm` : "–"}}</td>
                </tr>
                <tr>
                  <th>Bootsklasse(n)</th>
                  <td>{{ data.boat_class }}</td>
                </tr>
                <tr>
                  <th>Disziplin(en)</th>
                  <td>
                    <p>
                      <template v-for="(item, idx) in data.disciplines">
                        <template v-if="idx < data.disciplines.length - 1">
                          {{ item }},
                        </template>
                        <template v-else>
                          {{ item }}
                        </template>
                      </template>
                    </p>
                  </td>
                </tr>
                <tr>
                  <th>Rennanzahl</th>
                  <td>{{ data.num_of_races }}</td>
                </tr>
                <tr>
                  <th>Medaillen Gesamt</th>
                  <td>{{ data.medals_total }}</td>
                </tr>
                <tr>
                  <th>Medaillen Gold</th>
                  <td>{{ data.medals_gold }}</td>
                </tr>
                <tr>
                  <th>Medaillen Silber</th>
                  <td>{{ data.medals_silver }}</td>
                </tr>
                <tr>
                  <th>Medaillen Bronze</th>
                  <td>{{ data.medals_bronze }}</td>
                </tr>
                <tr>
                  <th>Finale A</th>
                  <td>{{ data.final_a }}</td>
                </tr>
                <tr>
                  <th>Finale B</th>
                  <td>{{ data.final_b }}</td>
                </tr>
                </tbody>
              </v-table>
            </v-col>
            <v-col v-if="!mobile">
              <h2>Rennliste</h2>
              <v-table class="tableStyles" density="compact">
                <thead>
                <tr>
                  <th class="px-1">Wettkampf</th>
                  <th class="px-1">Startzeit</th>
                  <th class="px-1">Platz</th>
                  <th class="px-1">Ort</th>
                  <th class="px-1">Lauf</th>
                  <th class="px-1">Disziplin</th>
                </tr>
                </thead>
                <tbody class="nth-grey">
                <tr v-for="(race, idx) in data.race_list">
                  <td>{{ race.name }}</td>
                  <td>{{ race.start_time }}</td>
                  <td>{{ race.rank }}</td>
                  <td>{{ race.venue }}</td>
                  <td>{{ race.race_phase }}</td>
                  <td>{{ race.boat_class }}</td>
                </tr>
                </tbody>
              </v-table>
            </v-col>
            <v-col cols="12" v-if="mobile" density="comfortable">
              <h2>Rennliste</h2>
              <v-table class="tableStyles">
                <thead>
                <tr>
                  <th class="px-1">Wettkampf</th>
                  <th class="px-1">Startzeit</th>
                  <th class="px-1">Platz</th>
                  <th class="px-1">Ort</th>
                  <th class="px-1">Bootsklasse</th>
                </tr>
                </thead>
                <tbody class="nth-grey">
                <tr v-for="(race, idx) in data.race_list">
                  <td>{{ race.name }}</td>
                  <td>{{ race.start_time }}</td>
                  <td>{{ race.rank }}</td>
                  <td>{{ race.venue }}</td>
                  <td>{{ race.boat_class }}</td>
                </tr>
                </tbody>
              </v-table>
            </v-col>
          </v-row>
        </v-container>
      </v-container>
    </v-layout>
  </v-card>
</template>

<script setup>
import AthletenFilter from "@/components/filters/athletenFilter.vue";
</script>

<script>
import {mapState} from "pinia";
import {useAthletenState} from "@/stores/athletenStore";
import {useGlobalState} from "@/stores/globalStore";

export default {
  computed: {
    ...mapState(useGlobalState, {
      headerReduced: "getHeaderReducedState"
    }),
    ...mapState(useAthletenState, {
      filterState: "getFilterState"
    }),
    ...mapState(useAthletenState, {
      tableData: "getTableData"
    }),
  },
  methods: {
    openPrintDialog() {
      window.print();
    },
    exportTableData() {
      const store = useAthletenState()
      store.exportTableData()
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useAthletenState()
      store.setFilterState(this.filterState)
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    },
    formatMilliseconds(ms) {
      if (ms) {
        return new Date(ms).toISOString().slice(14, -2)
      } else {
        return 0
      }
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();

    window.onload = () => {
      const url = new URL(window.location.href);
      const athlete_id = url.searchParams.get("athlete_id");
      if (athlete_id !== undefined && athlete_id !== null) {
        const store = useAthletenState()
        store.getAthlete({"id":athlete_id})
      }
    }
  },
  data() {
    return {
      mobile: false,
      filterOpen: this.filterState,
      data: []
    }
  },
  watch: {
    filterState(newValue) {
      this.filterOpen = newValue;
    },
    filterOpen: function (newVal, oldVal) {
      if (oldVal === true && newVal === false && this.filterState === true) {
        const store = useAthletenState()
        store.setFilterState(oldVal)
      }
    },
    tableData: function (newVal, ){
      this.data = newVal
    }
    /*
    tableData: function (newVal,) {
      if (newVal !== undefined) {
        router.push(this.$route.path + `?athlete_id=${newVal.id}`)
      }
    }
    */
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
    padding: 0 5px;
  }

  td {
    text-align: left;
    border: 0.5px solid #e0e0e0;
    padding: 0 5px;
  }
}

.nth-grey tr:nth-child(odd) {
  background-color: rgba(0, 0, 0, .05);
}

.v-table > .v-table__wrapper > table > tbody > tr > td {
  padding: 0 6px;
}

.v-table > .v-table__wrapper > table > tbody > tr > th {
  padding: 0 6px;
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
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}

@media print {
  i, .filterToggleButton, .filterToggleButtonMobile {
    display: none;
  }
}
</style>

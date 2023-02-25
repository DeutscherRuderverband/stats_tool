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
        <teams-filter/>
      </v-navigation-drawer>

      <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 py-0 main-container'">
        <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
          <h1>Teams</h1>
          <v-icon id="tooltip-teams-icon" color="grey" class="ml-2 v-icon--size-large">mdi-information-outline</v-icon>
          <v-tooltip
              activator="#tooltip-teams-icon"
              location="end"
              open-on-hover
          >Hier findet sich die Zusammensetzung der gewählten Nationalmannschaft
            einschließlich der Besetzung innerhalb der verschiedenen Bootsklassen.
          </v-tooltip>
          <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
          <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large">mdi-table-arrow-right</v-icon>
        </v-col>
        <v-divider></v-divider>

        <v-container v-if="loading" class="d-flex flex-column align-center">
          <v-progress-circular indeterminate color="blue" size="40" class="mt-15"></v-progress-circular>
          <div class="text-center" style="color: #1369b0">Lade Ergebnisse...</div>
        </v-container>

        <v-container class="pa-0 mt-2 pb-8" style="min-height: 400px" v-if="!loading && metaData.results">
          <v-row>
            <v-col cols="12">
              <h2>{{ metaData.nation }}</h2>
              <v-col :cols="mobile ? 12 : 8" class="pa-0">
                <v-alert type="success" variant="tonal" class="my-2" v-if="metaData.results">
                  <v-row>
                    <v-col cols="12">
                      <p><b>{{ metaData.results }} Datensätze |
                        Von {{ metaData["interval"][0] }}
                        bis {{ metaData["interval"][1] }}</b>
                      </p>
                      <p><b>Events: </b>{{filterConf.events}}</p>
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

              <v-col cols="12" class="pa-0">
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
                            <template v-for="(athlete, idx) in item">
                              <a v-if="idx < item.length - 1" :href="`/athleten?athlete_id=${athlete[1]}`"
                                 class="link-underline">
                                {{ athlete[0].replace(/,/g, '') }},
                              </a>
                              <a v-else :href="`/athleten?athlete_id=${athlete[1]}`" class="link-underline">
                                {{ athlete[0].replace(/,/g, '') }}
                              </a>
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
import {mapState} from "pinia";
import {useTeamsState} from "@/stores/teamsStore";
import {useGlobalState} from "@/stores/globalStore";

export default {
  computed: {
    ...mapState(useGlobalState, {
      headerReduced: "getHeaderReducedState"
    }),
    ...mapState(useTeamsState, {
      filterState: "getFilterState"
    }),
    ...mapState(useTeamsState, {
      metaData: "getMetaData"
    }),
    ...mapState(useTeamsState, {
      tableData: "getTableData"
    }),
    ...mapState(useTeamsState, {
      loading: "getLoadingState"
    }),
    ...mapState(useTeamsState, {
      filterConf: "getFilterConfig"
    }),
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
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
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
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}

@media print {
  i, .filterToggleButton, .filterToggleButtonMobile {
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
</style>

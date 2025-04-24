<template>

  <!--LOADING-->
  <div v-if="loading">
    <v-progress-circular class="pa-0 mt-3" indeterminate color="blue" size="40"></v-progress-circular>
  </div>

  <!-- MULTIPLE -->
  <v-container v-if="!loading" class="px-0 pt-4">

    <div v-if="!boatClassData">
      <v-container class="pa-0 mt-3">
        <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
            Bitte wähle ein Jahr und ein Event in dem Filter auf der linken Seite.
        </v-alert>
    </v-container>

    </div>

    <div v-else>

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
          <v-radio color="blue" :label="`${boatClassData.wbt} (WBT)`" value="wbt" @click="setRelationTimeFrom('wbt')"
            :disabled="boatClassData.wbt == '00:00.00'"></v-radio>
          <v-radio color="blue" :label="`${boatClassData.wbt_oz} (WBT vor OZ)`" value="ozt"
            @click="setRelationTimeFrom('ozt')" :disabled="boatClassData.wbt_oz == '00:00.00'"></v-radio>
        </v-radio-group>
      </v-col>

    </v-row>

    <v-table class="tableStyles" density="compact">
      <thead>
        <tr>
          <th v-for="tableHead in multipleTableData[0]" class="px-2">
            <p>{{ tableHead.text }}<v-tooltip activator="parent" location="bottom" v-if="tableHead.tooltip != null">{{
              tableHead.tooltip }}</v-tooltip></p>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(country, idx) in multipleTableData.slice(1)">
          <td v-for="item in country" :key="item" class="px-2">
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
          :items="getMultipleChartOptions.groups" v-model="getMultipleChartOptions.groups_in_chart" variant="outlined">
        </v-select>
      </v-col>
    </v-row>

    <!-- Graphen -->
    <v-row class="mt-0 pt-0">
      <v-col :cols="mobile ? 12 : 6" class="pa-0">
        <v-container :class="mobile ? 'pa-0' : 'pa-2'">
          <LineChart :data="getMeanPacingProfiles" :chartOptions="chartMetadata[0]" class="chart-bg">
          </LineChart>
        </v-container>

        <v-container :class="mobile ? 'pa-0' : 'pa-2'">
          <LineChart :data="getMeanGPsData[2]" :chartOptions="chartMetadata[1]" class="chart-bg">
          </LineChart>
        </v-container>

        <v-container :class="mobile ? 'pa-0' : 'pa-2'">
          <LineChart :data="getMeanIntermediateData" :chartOptions="chartMetadata[2]" class="chart-bg">
          </LineChart>
        </v-container>
      </v-col>

      <v-col :cols="mobile ? 12 : 6" class="pa-0">
        <v-container :class="mobile ? 'pa-0' : 'pa-2'">
          <LineChart :data="getMeanGPsData[0]" :chartOptions="chartMetadata[3]" class="chart-bg">
          </LineChart>
        </v-container>

        <v-container :class="mobile ? 'pa-0' : 'pa-2'">
          <LineChart :data="getMeanGPsData[1]" :chartOptions="chartMetadata[4]" class="chart-bg">
          </LineChart>
        </v-container>

      </v-col>
    </v-row>

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

export default {
  computed: {
  ...mapState(useRennstrukturAnalyseState, {
    loading: "getLoadingState",
    wbt: "getRelationTimeFrom",
    boatClassData: "getBoatClassData",
    multipleTableData: "getMultipleTableData",
    getMeanGPsData: "getMeanGPSChartData",
    getMeanIntermediateData: "getMeanIntermediateChartData",
    getMeanPacingProfiles: "getMeanPacingProfiles",
    getMultipleChartOptions: "getMultipleOptions",
    chartMetadata: "getMultipleChartMetadata",
  }),
},
  data() {
    return {
      mobile: false,
      radios: "wbt",
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
    this.radios = this.wbt

  },
  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    },
    setRelationTimeFrom(value) {
      useRennstrukturAnalyseState().setRelationTimeFrom(value);
    }
  },
  watch: {
    radios(newValue) {
      const store = useRennstrukturAnalyseState()
      store.setRelationTimeFrom(newValue)
    },
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

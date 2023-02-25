<template>
  <v-card style="box-shadow: none; z-index: 1">
    <v-layout>
      <v-navigation-drawer
          permanent
          :location="mobile ? 'bottom' : 'left'"
          @mouseover="hoverFilter = true"
          @mouseleave="hoverFilter = false"
          expand-on-hover
          rail
          style="margin-top: 160px; background-color: white"
          width="500">
        <v-container class="pa-4" v-bind:style='{"height" : (hoverFilter ? "1200px" : "100%")}'>
          <h2 v-if="hoverFilter">Filter Funktionen</h2>
          <v-icon v-if="!hoverFilter">mdi-filter</v-icon>
          <transition name="fade">
          <v-form v-show="hoverFilter">
            <v-label>Year</v-label>
            <v-container class="pa-0 pt-1 d-flex flex-row">
              <v-text-field label="Start" value="1950" class="mr-2" density="compact" validation-value="number"/>
              <v-text-field label="End" value="2025" class="ml-2" density="compact" validation-value="number"/>
            </v-container>
            <v-label class="ma-1">Wettkampfklassen</v-label>
            <checkbox v-bind:checkboxDaten="auswahlWettkampfklassen"/>
            <v-label class="ma-1">Ergebnisse</v-label>
            <checkbox v-bind:checkboxDaten="auswahlErgebnisse"/>
            <v-container class="pa-0">
              <v-row no-gutters>
                <v-col v-for="(auswahl, idx) in auswahlRennkategorien" :key="idx">
                  <v-label class="ma-1">{{ auswahl.name }}</v-label>
                  <checkbox v-bind:checkboxDaten="auswahl.auswahl"/>
                </v-col>
              </v-row>
            </v-container>
            <v-label class="ma-1">Basis</v-label>
            <v-radio-group>
              <v-row no-gutters>
              <v-col>
                <v-radio label="500m" value="1"></v-radio>
                <v-radio label="1000m" value="2"></v-radio>
                <v-radio label="2000m" value="3"></v-radio>
              </v-col>
              <v-col>
                <v-radio label="m/s" value="4"></v-radio>
                <v-radio label="km/h" value="5"></v-radio>
                <v-radio label="mph" value="6"></v-radio>
              </v-col>
                </v-row >
            </v-radio-group>
            <v-container class="pa-0 pt-6 text-right">
              <v-btn color="grey" class="mx-2"><v-icon>mdi-backspace-outline</v-icon></v-btn>
              <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
            </v-container>
          </v-form>
          </transition>
        </v-container>
      </v-navigation-drawer>
    </v-layout>
  </v-card>
</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";

export default {
  components: {Checkbox},
  data() {
    return {
      mobile: false,
      hoverFilter: false,
      auswahlWettkampfklassen: [
        { id: 1, name: 'European Championships', selected: false },
        { id: 2, name: 'Olympics', selected: false },
        { id: 3, name: 'Qualifications', selected: false },
        { id: 4, name: 'World Championships', selected: false },
        { id: 5, name: 'World Rowing Cup', selected: false },
      ],
      auswahlErgebnisse: [
        { id: 1, name: '1. Plätze (Gold-Standard, GS)', selected: false },
        { id: 2, name: 'Plätze 1-3', selected: false },
        { id: 3, name: 'Podium-Standard PS (Zeit zum Erreichen einer Medaille)', selected: false },
      ],
      auswahlRennkategorien: [
        {
          name: "Finals",
          auswahl: [
              { id: 1, name: 'FA', selected: false },
              { id: 2, name: 'FB', selected: false },
              { id: 3, name: 'FC', selected: false },
              { id: 4, name: 'FC', selected: false },
              { id: 4, name: 'F...', selected: false }
          ]
        },
        {
          name: "Halbfinals",
          auswahl: [
              { id: 1, name: 'SA/B SA/', selected: false },
              { id: 2, name: 'BB', selected: false },
              { id: 3, name: 'SC/D', selected: false },
              { id: 4, name: 'SD/E/F', selected: false },
              { id: 4, name: 'S...', selected: false }
          ]
        },
        {
          name: "Viertelfinals",
          auswahl: [
              { id: 1, name: 'Q1-4', selected: false },
              { id: 2, name: 'Q5-8', selected: false }
          ]
        }
      ]
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },

  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890;
    }
  }
}

</script>
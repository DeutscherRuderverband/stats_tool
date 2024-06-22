<template>
  <v-container :style="{ 'overflow-y': 'auto' }">
    <v-row>
      <v-col>
        <h2>Filter</h2>
      </v-col>
      <v-col class="text-right">
        <i class="mdi mdi-close" style="font-size: 25px; color: darkgrey" @click="hideFilter"></i>
      </v-col>
    </v-row>
    <v-divider></v-divider>

    <!-- Single - Multiple-->
    <v-tabs fixed-tabs v-model="tab" bg-color="blue">
      <v-tab value="one" :class="{ inactive: tab === 'two' }">Single</v-tab>
      <v-tab value="two" :class="{ inactive: tab === 'one' }">Multiple</v-tab>
    </v-tabs>

    <v-tabs-window v-model="tab">
      <!-- SINGLE RACE -->
      <v-tabs-window-item v-if="tab === 'one'">
        <v-form id="rennstrukturFilterFormular" class="mt-2" @submit.prevent="onSubmit" ref="filterForm"
          v-model="formValid" lazy-validation>
          <!-- Year -->
          <v-select class="pt-4" clearable density="comfortable" label="Jahr" :items="optionsYear"
            v-model="selectedYear" variant="outlined" :rules="[v => !!v || 'Wähle ein Jahr']"></v-select>
          <!-- Competitions -->
          <v-select class="pt-3" density="comfortable" label="Event" :items="optionsCompetitions"
            v-model="selectedCompetitions" variant="outlined"></v-select>
          <v-container class="pa-0 pt-6 text-right">
            <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
          </v-container>
        </v-form>
      </v-tabs-window-item>

      <!-- MULIPLE RACES -->
      <v-tabs-window-item v-if="tab === 'two'">
        <v-form id="rennstrukturFilterFormular2" class="mt-2" @submit.prevent="onMultipleSubmit" ref="filterForm2"
          v-model="formValid2" lazy-validation>
          <!-- Gender-->
          <v-chip-group multiple color="blue" v-model="selectedGenders">
            <v-chip v-for="genderType in optionsGender">{{ genderType }}
            </v-chip>
          </v-chip-group>

          <!-- Gender-->
          <v-chip-group multiple color="blue" v-model="selectedAges">
            <v-chip v-for="ageGroup in optionsAges">{{ ageGroup }}
            </v-chip>
          </v-chip-group>


          <!-- Bootsklasse-->
          <v-select class="pt-3" density="comfortable" label="Bootsklasse" :items="optionsBoatClass"
            v-model="selectedBoatClass" variant="outlined"></v-select>

          <!--
            <v-container class="pa-0 text-right">
            <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
          </v-container>
          -->

          <h3>Gruppenfilter</h3>

          <!-- Group expansion panels-->
          <v-expansion-panels multiple class="pt-2">
            <v-expansion-panel v-for="(panel, index) in panels" :key="index" class="expansion-panel">
              <v-expansion-panel-title>{{ panel.title }}</v-expansion-panel-title>
              <v-expansion-panel-text>

                <!-- Year -->
                <v-container class="pa-0 d-flex pt-3">
                  <!-- Start Year-->
                  <v-col cols="6" class="pa-0 pr-2">
                    <v-select clearable label="Von" :items="optionsYear" variant="outlined" v-model="panel.startYear"
                      density="comfortable"
                      :rules="[v => !!v || 'Wähle ein Jahr als Anfangswert',
                      (v) => parseInt(v) <= parseInt(endYear) || 'Zeitraum Anfang darf nicht nach dem Ende liegen.']"></v-select>
                  </v-col>
                  <!-- End Year-->
                  <v-col cols="6" class="pa-0 pl-2">
                    <v-select clearable label="Bis" :items="optionsYear" v-model="panel.endYear" variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || 'Wähle ein Jahr als Endwert',
                      (v) => parseInt(v) >= parseInt(startYear) || 'Zeitraum Ende darf nicht vor dem Anfang liegen.']"></v-select>
                  </v-col>
                </v-container>

                <!-- Country -->
                <v-select label="Nation" class="pt-2" clearable :items="optionsCountry" v-model="panel.selectedCountry"
                  variant="outlined">
                </v-select>

                <!-- Competions -->
                <v-select class="pt-3" chips multiple density="comfortable" label="Event(s)"
                  :items="optionsCompetitions" v-model="panel.selectedCompetitions" variant="outlined">
                </v-select>

                <!-- Phase (final, semifinal, ...) -->
                <v-select label="Lauf" class="pt-2" clearable :items="optionsPhases" v-model="panel.selectedPhases" multiple
                  variant="outlined" chips>
                </v-select>

                <!--Placements -->
                <v-select label="Platzierung" class="pt-2" clearable :items="optionsPlacements"
                  v-model="panel.selectedPlacements" multiple variant="outlined" chips
                  :rules="[v => v.length > 0 || 'Wähle mindestens eine Laufkategorie']">
                </v-select>


                <!-- Races (calculated based on other filters) -->
                <!-- To do show selected count-->
                <!-- 
                <v-row>
                  <v-col>
                    <h3>Ausgewählte Rennen:</h3>
                  </v-col>
                  <v-col class="text-right">
                    <v-btn color="blue" class="mx-2" size="small">Aktualisieren</v-btn>
                  </v-col>
                </v-row>

                
                <v-select label="Rennen" class="pt-4" clearable :items="optionsRaces" v-model="selectedRaces" multiple
                  variant="outlined">
                </v-select>

                -->

              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- Buttons (Remove or Add group) -->
          <v-row class="pt-2">
            <v-col>
              <v-btn @click="removePanel" width="50%" size="small" color="#EEEEEE"
                prepend-icon="mdi-cancel">Entfernen</v-btn>
              <v-btn @click="addPanel" width="50%" size="small" color="#EEEEEE"
                prepend-icon="mdi-plus">Hinzufügen</v-btn>
            </v-col>
          </v-row>

          <!-- Alert, when more than 6 groups-->
          <v-alert v-if="alertVisible" class="mt-2" border-color="info" border="top" closable>
            Maximal 6 Gruppen
          </v-alert>

          <v-container class="pt-6 pa-0 pb-100 mb-100 text-right">
            <v-btn color="blue" class="mx-2" type="submit">Bestätigen</v-btn>
          </v-container>


        </v-form>
        <div class="padding"></div> <!-- Added so scrolling works correctly-->
      </v-tabs-window-item>
    </v-tabs-window>
  </v-container>

</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";
import { useRennstrukturAnalyseState } from "@/stores/baseStore";
import { mapState } from "pinia";

export default {
  components: { Checkbox},
  computed: {
    ...mapState(useRennstrukturAnalyseState, {
      raceAnalysisFilterOptions: "getRaceAnalysisFilterOptions"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      showFilter: "getFilterState"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      multiple: "getMultiple"
    }),

  },
  data() {
    return {

      tab: "one",

      //Gender
      optionsGender: [],
      selectedGenders: [0],

      //Age Group
      optionsAges: [],
      selectedAges: [2],

      //Boat class
      optionsBoatClass: [],
      selectedBoatClass: "M1x",

      //Year
      //startYear: 2020,
      //endYear: 2024,
      selectedYear: new Date().getFullYear(), //For single filter
      optionsYear: [2020, 2021, 2022, 2023, 2024, 2025],

      //Country
      optionsCountry: ['GER', 'HUN', 'USA', 'FRA'],
      //selectedCountry: 'GER',

      //Competition
      selectedCompetitions: ["WCH"], // list of dicts with objects containing displayName, id and key
      optionsCompetitions: ["WCH", "WCp 1", "Wcp 2", "Wcp 3"],
      compTypes: [], // list of dicts with objects containing displayName, id and key

      //Phase
      //selectedPhases: ["final", "semifinal", "qualifying"],
      optionsPhases: [],

      //Placement
      optionsPlacements: [],
      //selectedPlacements: [1,2,3,4,5,6],

      //Races
      optionsRaces: [],
      selectedRaces: [],

      mobile: false,
      hoverFilter: false,
      drawer: null,
      formValid: true,
      formValid2: true,

      panels: [
        { title: 'Gruppe 1', startYear: 2020, endYear: 2025, selectedCountry: "GER (Germany)", selectedCompetitions: ["WCH", "WCp 1", "WCp 2", "WCp 3"],
         selectedPhases: ["final", "semifinal"], selectedPlacements: [1,2,3,4,5,6], optionsRaces: [] },
      ],
      alertVisible: false,

    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();

    const store = useRennstrukturAnalyseState() //DELETE?
    const setFilterValues = async () => {
      this.raceAnalysisFilterOptions = await store.getFilterOptions() //DELETE?
      // Boat class
      this.optionsGender = Object.keys(this.raceAnalysisFilterOptions.boat_classes)
      this.optionsGender.pop() //Remove the all option
      for (let ageGroup in this.raceAnalysisFilterOptions.boat_classes.m) {
        //console.log(ageGroup)
        this.optionsAges.push(ageGroup)
        if (ageGroup == "elite") {
          for (let boatClass in this.raceAnalysisFilterOptions.boat_classes.m[ageGroup]) {
          this.optionsBoatClass.push(this.raceAnalysisFilterOptions.boat_classes.m[ageGroup][boatClass][0]);
          //console.log(boatClass)
        }
        }
      }

      // year
      this.startYear = this.raceAnalysisFilterOptions.years[0]
      this.endYear = this.raceAnalysisFilterOptions.years[1]
      this.optionsYear = Array.from({length: this.endYear - this.startYear + 1}, (_, i) => this.endYear - i)
      
      // nation_code
      let countryCodes = Object.keys(this.raceAnalysisFilterOptions.nations)
      let countryNames = Object.values(this.raceAnalysisFilterOptions.nations)
      let finalCountryNames = []
      for (const [idx, countryCode] of countryCodes.entries()) {
        finalCountryNames.push(countryCode + " (" + countryNames[idx] + ")")
      }
      this.optionsCountry = finalCountryNames

      // competition category id
      this.compTypes = this.raceAnalysisFilterOptions.competition_categories
      this.optionsCompetitions = this.compTypes.map(item => item.display_name)

      // Runs
      this.optionsPhases = this.raceAnalysisFilterOptions.runs
      
      // Placement
      this.optionsPlacements = this.raceAnalysisFilterOptions.ranks
    }
    setFilterValues()

  },
  methods: {

    async onSubmit() {
      const {valid} = await this.$refs.filterForm.validate()
      if (valid) {
        this.hideFilter()
        this.submitFormData()
      } else {
        alert("Bitte überprüfen Sie die Eingaben.")
      }
    },
    //TODO Check Form Validation
    async onMultipleSubmit() {
      const {valid} = await this.$refs.filterForm2.validate()
      if (valid) {
        console.log("Multiple Form Submitted")
        this.hideFilter()
        this.submitMultipleFormData()
      } else {
        alert("Bitte überprüfen Sie die Eingaben.")
      }
    },
    submitFormData() {
      const store = useRennstrukturAnalyseState()
      store.setToLoadingState()
      const data = {
        "year": this.selectedYear,
        "competition_type": this.compTypes.filter(item =>
            this.selectedCompetitions.includes(item.display_name)).map(item => item.id)[0]
      }
      return store.postFormData(data).then(() => {
        console.log("Form data sent...")
      }).catch(error => {
        console.error(error)
      });
    },
    submitMultipleFormData() {
      const store = useRennstrukturAnalyseState()
      store.setToLoadingState()
      const groups = []
      for (const panel of this.panels) {
        const groupData = {
          "start_year": panel.startYear,
          "end_year": panel.endYear,
          "country": panel.selectedCountry.slice(0, 3),
          "events": panel.selectedCompetitions,
          "phases": panel.selectedPhases,
          "placements": panel.selectedPlacements
        }
        groups.push(groupData)
      }
      console.log("This is the Group data")
      console.log(groups)
      const data = {
        "boat_class": this.selectedBoatClass,
        "groups": groups
      }
      return store.postMultipleFormData(data).then(() => {
        console.log("Multiple Form data sent...")
      }).catch(error => {
        console.error(error)
      });
    },

    addPanel() {
      const newIndex = this.panels.length + 1;
      if (this.panels.length < 6) {
        this.panels.push({ title: `Gruppe ${newIndex}`, startYear: 2020, endYear: 2025, selectedCountry: "GER (Germany)", selectedCompetitions: ["WCH", "WCp 1", "WCp 2", "WCp 3"],
        selectedPhases: ["final", "semifinal"], selectedPlacements: [1,2,3,4,5,6], optionsRaces: [] });
      }
      else {
        this.alertVisible = true;
        setTimeout(() => {
          this.alertVisible = false;
        }, 5000);
      }

    },

    removePanel() {
      this.panels.pop();
    },

    hideFilter() {
      const store = useRennstrukturAnalyseState()
      store.setFilterState(this.showFilter)
    },

    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890;
    },

    updateBoatClass() {
      //Map Gender
      const genderMapping = {0: "m", 1: "w", 2: "mixed"};
      let selectedGendersValue = this.selectedGenders.map(value => genderMapping[value])

      //Map Age
      const ageMapping = {0: "u19", 1: "u23", 2: "elite", 3: "para"};
      let selectedAgesValue = this.selectedAges.map(value => ageMapping[value])

      this.optionsBoatClass = []

      //Gender Loop
      for (const gender of selectedGendersValue) {
        //Age Grpup
        for (const age of selectedAgesValue) {
          //Category
          for(const category in this.raceAnalysisFilterOptions.boat_classes[gender][age]) {
            const boatClass = this.raceAnalysisFilterOptions.boat_classes[gender][age][category][0]
            this.optionsBoatClass.push(boatClass)
          }
        }
      }
    }
  },
  watch: {
    selectedGenders: function () {
      this.updateBoatClass()
    },
    selectedAges: function () {
      this.updateBoatClass()
    }
  }
}

</script>

<style scoped>
.mdi-close:hover {
  cursor: pointer;
}

.inactive {
  background-color: #EEEEEE;
  /* Change to your desired active background color */
  color: #000;
  /* Change text color if needed */
}

.padding {
  padding-top: 180px;
  /* Adds 20 pixels of padding at the bottom */
  color: white
}
</style>
<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Filter</h2>
      </v-col>
      <v-col class="text-right">
        <i class="mdi mdi-close" style="font-size: 25px; color: darkgrey" @click="hideFilter"></i>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-form class="mt-2" id="berichteFilterFormular" @submit.prevent="onSubmit"
            v-model="formValid" lazy-validation ref="filterForm">
      <v-container class="pa-0 d-flex pt-3">
        <v-col cols="6" class="pa-0 pr-2">
          <v-select clearable label="Von" :items="optionsStartYear"
                    variant="outlined" v-model="startYear" density="comfortable"
                    :rules="[v => !!v || 'Wähle ein Jahr als Anfangswert',
                    (v) => parseInt(v) <= parseInt(endYear) || 'Zeitraum Anfang darf nicht nach dem Ende liegen.']"
          ></v-select>
        </v-col>
        <v-col cols="6" class="pa-0 pl-2">
          <v-select clearable label="Bis" :items="optionsEndYear"
                    v-model="endYear" variant="outlined" density="comfortable"
                    :rules="[v => !!v || 'Wähle ein Jahr als Endwert',
                        (v) => parseInt(v) >= parseInt(startYear) || 'Zeitraum Ende darf nicht vor dem Anfang liegen.']"
          ></v-select>
        </v-col>
      </v-container>
      <v-select class="pt-2" clearable chips multiple color="blue"
                label="Event(s)" :items="optionsCompTypes"
                v-model="selectedCompTypes" variant="outlined"
                :rules="[v => v.length > 0 || 'Wähle mindestens eine Wettkampfklasse']"
      ></v-select>
      <v-autocomplete class="pt-4" :items="optionsNations" clearable multiple chips v-model="selectedNation"
                      variant="outlined" color="blue" label="Nation(en)" density="comfortable"
                      :rules="[v => !!v || 'Wähle mindestens eine Nation']"
      ></v-autocomplete>
      <!--
      <v-label>Bootsklasse</v-label>
      <v-chip-group filter color="blue" v-model="selectedGenders">
        <v-chip v-for="genderType in genderTypeOptions">{{ genderType.charAt(0).toUpperCase() + genderType.slice(1) }}
        </v-chip>
      </v-chip-group>
      <v-chip-group filter color="blue" v-model="selectedAgeGroups">
        <v-chip v-for="ageGroup in ageGroupOptions">{{ ageGroup.charAt(0).toUpperCase() + ageGroup.slice(1) }}</v-chip>
      </v-chip-group>
      <v-select class="pt-3" label="Bootsklassen" clearable chips density="comfortable"
                :items="optionsBoatClasses" v-model="selectedBoatClasses" variant="outlined"
                :rules="[v => !!v || 'Wähle mindestens eine Bootsklasse']"
      ></v-select>
      -->
      <!--
      <v-chip-group filter color="blue" v-model="selectedMedalTypes">
        <v-chip v-for="medalType in optionsMedalTypes">{{ medalType }}</v-chip>
      </v-chip-group>
      <v-select class="pt-3" label="Bootsklassen" clearable multiple chips density="comfortable"
                :items="optionsBoatClasses" v-model="selectedBoatClasses" variant="outlined"
                :rules="[v => !!v || 'Wähle mindestens eine Bootsklasse']"
      ></v-select>
      -->

      <v-container class="pa-0 pt-8 text-right">
        <v-btn color="grey" class="mx-2" @click="clearFormInputs">
          <v-icon>mdi-backspace-outline</v-icon>
        </v-btn>
        <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
      </v-container>
    </v-form>
  </v-container>
</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";
import {mapState} from "pinia";
import {useMedaillenspiegelState} from "@/stores/medaillenspiegelStore";

export default {
  components: {Checkbox},
  computed: {
    ...mapState(useMedaillenspiegelState, {
      filterOptions: "getMedaillenspiegelFilterOptions"
    }),
    ...mapState(useMedaillenspiegelState, {
      showFilter: "getFilterState"
    }),
  },
  data() {
    return {
      // api filter data
      filterData: [],
      // general
      mobile: false,
      hoverFilter: false,
      drawer: null,
      formValid: true,

      // competition type
      compTypes: [],
      optionsCompTypes: [],
      selectedCompTypes: ["WCH", "WCp 1", "WCp 2", "WCp 3", "OG"],

      // year
      startYear: 0,
      endYear: 0,
      optionsStartYear: [],
      optionsEndYear: [],

      // medal types
      optionsMedalTypes: [],
      selectedMedalTypes: [0],

      // nations
      optionsNations: [],
      selectedNation: [
        "ITA (Italy)",
        "GER (Germany)",
        "GBR (Great Britain)",
        "USA (United States)",
        "AUS (Australia)",
        "NZL (New Zealand)",
        "ROU (Romania)",
        "FRA (France)"
      ],
      // boat classes
      optionsBoatClasses: [],
      selectedBoatClasses: this.optionsBoatClasses,
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen)
    this.checkScreen()

    // fetch filter configuration
    const store = useMedaillenspiegelState()
    store.fetchMedaillenspiegelFilterOptions()
    this.initializeFilter(this.filterOptions[0])
  },
  methods: {
    initializeFilter(data) {
      this.startYear = Object.values(data.years[0])[0]
      this.endYear = Object.values(data.years[1])[0]
      this.optionsStartYear = Array.from({length: this.endYear - this.startYear + 1}, (_, i) => this.startYear + i)
      this.optionsEndYear = Array.from({length: this.endYear - this.startYear + 1}, (_, i) => this.endYear - i)
      // competition category id
      this.compTypes = data.competition_categories
      this.optionsCompTypes = this.compTypes.map(item => item.display_name)
      // medal types
      this.optionsMedalTypes = data.medal_types.map(item => item.display_name)
      // nation_code
      let countryCodes = Object.keys(data.nations)
      let countryNames = Object.values(data.nations)
      let finalCountryNames = []
      for (const [idx, countryCode] of countryCodes.entries()) {
        finalCountryNames.push(countryCode + " (" + countryNames[idx] + ")")
      }
      this.optionsNations = finalCountryNames
      // boat classes
      let boatClassValues = []

      function getMostInnerValue(o) {
        for (let key in o) {
          if (typeof o[key] === 'object') {
            getMostInnerValue(o[key]);
          } else {
            boatClassValues.push(o[key]);
          }
        }
      }

      getMostInnerValue(Object.values(data.boat_classes))
      this.selectedBoatClasses = boatClassValues[0]
      this.optionsBoatClasses = boatClassValues

      if (this.startYear && this.endYear && this.selectedNation) {
        const store = useMedaillenspiegelState()
        store.postFormData({
              "years": [this.startYear, this.endYear],
              "gender": this.selectedGenders,
              "competition_type": this.compTypes.filter(item => this.selectedCompTypes.includes(item.display_name)).map(item => item.id),
              "nations": Array.isArray(this.selectedNation) ? this.selectedNation : [this.selectedNation],
              "types": this.selectedMedalTypes
            }
        )
      }
    },
    async onSubmit() {
      const {valid} = await this.$refs.filterForm.validate()
      if (valid) {
        this.hideFilter()
        await this.submitFormData()
      } else {
        alert("Bitte überprüfen Sie die Eingaben.")
      }
    },
    hideFilter() {
      const store = useMedaillenspiegelState()
      store.setFilterState(this.showFilter)
    },
    submitFormData() {
      const store = useMedaillenspiegelState()
      const data = {
        "years": [this.startYear, this.endYear],
        "gender": this.selectedGenders,
        "competition_type": this.compTypes.filter(item => this.selectedCompTypes.includes(item.display_name)).map(item => item.id),
        "nations": Array.isArray(this.selectedNation) ? this.selectedNation : [this.selectedNation],
        "types": this.selectedMedalTypes
      }

      return store.postFormData(data).then(() => {
        console.log("Form data sent...")
      }).catch(error => {
        console.error(error)
      })
    },
    clearFormInputs() {
      this.startYear = Object.values(this.filterOptions[0].years[0])[0]
      this.endYear = Object.values(this.filterOptions[0].years[1])[0]
      this.selectedCompTypes = ["WCH"]
      this.selectedNation = "GER (Germany))"
    },
    checkScreen() {
      this.windowWidth = window.innerWidth
      this.mobile = this.windowWidth < 890
    }
  },
  watch: {
    async filterOptions(newVal,) {
      this.filterData = newVal[0]
    },
    filterData: function (newVal,) {
      this.initializeFilter(newVal)
    }
  }
}

</script>

<style scoped>
.mdi-close:hover {
  cursor: pointer;
}
</style>

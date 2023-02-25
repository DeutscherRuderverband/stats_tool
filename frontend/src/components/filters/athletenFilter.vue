<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Suche</h2>
      </v-col>
      <v-col class="text-right">
        <i class="mdi mdi-close" style="font-size: 25px; color: darkgrey" @click="hideFilter"></i>
      </v-col>
    </v-row>
    <v-form class="mt-2" id="athletenFilterFormular"
            v-model="formValid" lazy-validation
            @submit.prevent="onSubmit" ref="filterForm">
      <v-autocomplete :items="previewAthleteResults.map(athlete => athlete.name)" v-model="selectedAthlete" clearable
                      variant="outlined" color="blue" label="Athlet" @input="searchAthletes"
                      class="pt-2" :rules="[v => !!v || 'Athletenname darf nicht leer sein']"
                      autofocus
      ></v-autocomplete>
      <h2 class="pt-3">Filter</h2>
      <v-divider></v-divider>
      <v-row class="pt-4">
        <v-col>
          <v-autocomplete :items="optionsNations" v-model="selectedNation"
                          variant="outlined" color="blue" label="Nation (optional)" clearable
                          density="comfortable"
          ></v-autocomplete>
        </v-col>
        <v-col>
          <v-select clearable :items="optionsBirthYear" variant="outlined"
                    v-model="selectedBirthYear" label="Jahrgang (optional)" density="comfortable"
          ></v-select>
        </v-col>
      </v-row>
      <v-chip-group filter color="blue" v-model="selectedGenders">
        <v-chip v-for="genderType in genderTypeOptions">{{ genderType.charAt(0).toUpperCase() + genderType.slice(1) }}
        </v-chip>
      </v-chip-group>
      <v-chip-group filter color="blue" v-model="selectedAgeGroups">
        <v-chip v-for="ageGroup in ageGroupOptions">{{ ageGroup.charAt(0).toUpperCase() + ageGroup.slice(1) }}</v-chip>
      </v-chip-group>
      <v-chip-group filter color="blue" v-model="selectedDiscipline">
        <v-chip v-for="discipline in optionsDisciplines">{{ discipline }}</v-chip>
      </v-chip-group>
      <v-select class="pt-3" label="Bootsklasse (optional)" clearable chips density="comfortable"
                :items="optionsBoatClasses" v-model="selectedBoatClasses" variant="outlined"
      ></v-select>
      <v-container class="pa-0 pt-8 text-right">
        <v-btn color="grey" class="mx-2" @click="clearFormInputs">
          <v-icon>mdi-backspace-outline</v-icon>
        </v-btn>
        <v-btn color="blue" class="mx-2" type="submit" @click="setFilterState">Übernehmen</v-btn>
      </v-container>
    </v-form>
  </v-container>
</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";
import {mapState} from "pinia";
import {useAthletenState} from "@/stores/athletenStore";
import router from "@/router";

export default {
  components: {Checkbox},
  computed: {
    ...mapState(useAthletenState, {
      previewAthleteResults: "getPreviewAthleteResults"
    }),
    ...mapState(useAthletenState, {
      filterOptions: "getAthletenFilterOptions"
    }),
    ...mapState(useAthletenState, {
      showFilter: "getFilterState"
    })
  },
  data() {
    return {
      filterData: [],
      // general
      mobile: false,
      hoverFilter: false,
      drawer: null,
      formValid: true,
      timeoutId: null,

      // athletes
      selectedAthlete: null,

      // year
      birthYear: null,
      optionsBirthYear: [],
      selectedBirthYear: null,

      // nations
      optionsNations: [],
      selectedNation: null,

      // boat classes
      boatClasses: {},
      genderTypeOptions: [],
      selectedGenders: [3],
      ageGroupOptions: [],
      selectedAgeGroups: 0,
      optionsDisciplines: [],
      selectedDiscipline: 0,
      optionsBoatClasses: [],
      selectedBoatClasses: this.optionsBoatClasses,
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen)
    this.checkScreen()

    const store = useAthletenState()
    store.fetchAthletesFilterOptions()
    this.initializeFilter(this.filterOptions[0])
  },
  methods: {
    initializeFilter(data) {
      //handle form data
      const startYear = Object.values(data.birth_years[0])[0]
      const endYear = Object.values(data.birth_years[1])[0]
      this.optionsBirthYear = Array.from({length: endYear - startYear + 1}, (_, i) => startYear + i)

      // nation_code
      let countryCodes = Object.keys(data.nations)
      let countryNames = Object.values(data.nations)
      let finalCountryNames = []
      for (const [idx, countryCode] of countryCodes.entries()) {
        finalCountryNames.push(countryCode + " (" + countryNames[idx] + ")")
      }
      this.optionsNations = finalCountryNames

      // boatclasses
      this.boatClasses = {}
      this.genderTypeOptions = Object.keys(data.boat_classes)
      let ageGroupOptions = Object.keys(data.boat_classes.m)
      ageGroupOptions.push(...Object.keys(data.boat_classes.w))
      this.ageGroupOptions = ageGroupOptions.filter((v, i, a) => a.indexOf(v) === i); // exclude non-unique values

      let boatClassOptions = []
      let values = Object.values(data.boat_classes)[0]
      Object.entries(values).forEach(([key, value], index) => {
        if (index === 0) {
          Object.entries(value).forEach(([, val]) => {
            if (typeof val === "object") {
              boatClassOptions.push(val[0])
              this.boatClasses[val[0]] = val[2]
            }
          })
        }
      });
      this.ageGroupOptions = []
      this.selectedBoatClasses = ["Alle"]
      this.optionsBoatClasses = boatClassOptions
    },
    searchAthletes(e) {
      const store = useAthletenState()
      const searchInput = e.target.value
      if (searchInput.length > 0) {
        clearTimeout(this.timeoutId)
        this.timeoutId = setTimeout(() => {
          store.postSearchAthlete({
            "search_query": searchInput,
            "nation": this.selectedNation,
            "birth_year": this.selectedBirthYear,
            "boat_class": this.boatClasses[this.selectedBoatClasses] || null
          })
        }, 450)
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
      const store = useAthletenState()
      store.setFilterState(this.showFilter)
    },
    submitFormData() {
      const store = useAthletenState()
      const athleteId = this.previewAthleteResults.find(item => item.name === this.selectedAthlete).id
      store.getAthlete({"id": athleteId}).then(() => {
        router.push(`/athleten?athlete_id=${athleteId}`)
      }).catch(error => {
        console.error(error)
      })
    },
    clearFormInputs() {
      this.selectedAthlete = null
      this.selectedNation = null
      this.selectedBirthYear = null
      this.selectedGenders = 3
      this.optionsDisciplines = []
      this.selectedBoatClasses = [0]
    },
    checkScreen() {
      this.windowWidth = window.innerWidth
      this.mobile = this.windowWidth < 890
    },
    setFilterState() {
      this.filterOpen = !this.filterOpen;
      const store = useAthletenState()
      store.setFilterState(this.filterState)
    },
  },
  watch: {
    selectedGenders: function (newVal,) {
      if (newVal !== undefined && this.filterData !== undefined) {
        this.selectedBoatClasses = null
        let optionsList = []
        if (newVal === 0) { // men
          optionsList.push(...Object.keys(this.filterData.boat_classes.m))
          this.optionsDisciplines = ["Skull", "Riemen"]
        }
        if (newVal === 1) { // women
          optionsList.push(...Object.keys(this.filterData.boat_classes.w))
          this.optionsDisciplines = ["Skull", "Riemen"]
        }
        if (newVal === 2) { // mixed
          optionsList = []
          let test = []
          for (const mixedOption of Object.values(this.filterData.boat_classes.mixed)) {
            test.push(Object.keys(mixedOption))
          }
          this.optionsBoatClasses = test.map(item => item[0]).flat()
          this.optionsDisciplines = ["Skull", "Riemen"]
        }
        if (newVal === 3) { // all
          this.ageGroupOptions = []
          this.optionsBoatClasses = ["Alle"]
          this.selectedBoatClasses = this.optionsBoatClasses
          this.optionsDisciplines = []
        }
        this.ageGroupOptions = optionsList.filter((v, i, a) => a.indexOf(v) === i); // exclude non-unique values
        let boatClassOptions = []
        Object.entries(Object.values(this.filterData.boat_classes)[newVal]).forEach(([key, value], index) => {
          if (index === this.selectedAgeGroups && this.selectedGenders !== 2) {
            Object.entries(value).forEach(([, val]) => {
              boatClassOptions.push(val[0])
              this.boatClasses[val[0]] = val[2]
            })
          } else if (this.selectedGenders === 2) {
            boatClassOptions.push(value[0])
            Object.entries(value).forEach(([, val]) => {
              this.boatClasses[val] = val[2]
            })
          }
        });
        if (newVal !== 3) {
          boatClassOptions = boatClassOptions.filter(item => this.selectedDiscipline ?
              !(item[item.length - 1] === 'x') : (item[item.length - 1] === 'x'))
          this.optionsBoatClasses = boatClassOptions
          this.selectedBoatClasses = boatClassOptions[0]
        }
      }
    },
    selectedAgeGroups: function (newVal,) {
      if (newVal !== undefined && this.filterData !== undefined) {
        this.selectedBoatClasses = null
        let genderObj = Object.values(this.filterData.boat_classes)[this.selectedGenders]
        let boatClassOptions = []
        Object.entries(genderObj).forEach(([key, value], index) => {
          if (index === newVal) {
            Object.entries(value).forEach(([, val]) => {
              boatClassOptions.push(val[0])
              this.boatClasses[val[0]] = val[2]
            })
          }
        });
        if (this.selectedGenders !== 3) {
          boatClassOptions = boatClassOptions.filter(item => this.selectedDiscipline ?
              !(item[item.length - 1] === 'x') : (item[item.length - 1] === 'x'))
          this.selectedBoatClasses = boatClassOptions[0]
          this.optionsBoatClasses = boatClassOptions
        }
      }
    },
    selectedDiscipline: function (newVal,) {
      if (newVal !== undefined && this.filterData !== undefined) {
        this.selectedBoatClasses = null
        let genderObj = Object.values(this.filterData.boat_classes)[this.selectedGenders]
        let boatClassOptions = []
        Object.entries(genderObj).forEach(([key, value], index) => {
          if (index === this.selectedAgeGroups && this.selectedGenders !== 2) {
            Object.entries(value).forEach(([, val]) => {
              boatClassOptions.push(val[0])
              this.boatClasses[val[0]] = val[2]
            })
          } else if (this.selectedGenders === 2) {
            boatClassOptions.push(value[0])
            Object.values(value).forEach((val) => {
              this.boatClasses[val[0]] = val[2]
            })
          }
        });
        boatClassOptions = boatClassOptions.filter(item => newVal ?
            !(item[item.length - 1] === 'x') : (item[item.length - 1] === 'x'))
        this.selectedBoatClasses = boatClassOptions[0]
        if (this.selectedGenders !== 3) {
          this.optionsBoatClasses = boatClassOptions
        }
      }
    },
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

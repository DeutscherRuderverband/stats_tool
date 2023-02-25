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
    <v-form id="rennstrukturFilterFormular" class="mt-2" @submit.prevent="onSubmit"
            ref="filterForm" v-model="formValid" lazy-validation>
      <v-select class="pt-2" clearable density="comfortable" label="Jahr"
                :items="optionsYear" v-model="selectedYear"
                variant="outlined" :rules="[v => !!v || 'Wähle ein Jahr']"
      ></v-select>
      <v-select class="pt-3" density="comfortable"
                label="Event" :items="optionsCompTypes"
                v-model="selectedCompTypes" variant="outlined"
      ></v-select>
      <v-container class="pa-0 pt-6 text-right">
        <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
      </v-container>
    </v-form>
  </v-container>
</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";
import {useRennstrukturAnalyseState} from "@/stores/baseStore";
import { mapState} from "pinia";

export default {
  components: {Checkbox},
  computed: {
    ...mapState(useRennstrukturAnalyseState, {
      raceAnalysisFilterOptions: "getRaceAnalysisFilterOptions"
    }),
    ...mapState(useRennstrukturAnalyseState, {
      showFilter: "getFilterState"
    }),
  },
  data() {
    return {
      competition_type: '',
      year: new Date().getFullYear(),
      gender: '',
      mobile: false,
      hoverFilter: false,
      drawer: null,
      formValid: true,

      // competition type
      compTypes: [], // list of dicts with objects containing displayName, id and key
      optionsCompTypes: [],
      selectedCompTypes: ["WCH"],
      // year
      optionsYear: [],
      selectedYear: new Date().getFullYear(),
      genders: ["männlich", "weiblich", "mixed"],
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();

    const store = useRennstrukturAnalyseState()

    const setFilterValues = async () => {
      this.raceAnalysisFilterOptions = await store.getFilterOptions()
      // year
      this.startYear = this.raceAnalysisFilterOptions.years[0]
      this.endYear = this.raceAnalysisFilterOptions.years[1]
      this.optionsYear = Array.from({length: this.endYear - this.startYear + 1}, (_, i) => this.endYear - i)

      // competition category id
      this.compTypes = this.raceAnalysisFilterOptions.competition_categories
      this.optionsCompTypes = this.compTypes.map(item => item.display_name)
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
    hideFilter() {
      const store = useRennstrukturAnalyseState()
      store.setFilterState(this.showFilter)
    },
    submitFormData() {
      const store = useRennstrukturAnalyseState()
      store.setToLoadingState()
      const data = {
        "year": this.selectedYear,
        "competition_type": this.compTypes.filter(item =>
            this.selectedCompTypes.includes(item.display_name)).map(item => item.id)[0]
      }
      return store.postFormData(data).then(() => {
        console.log("Form data sent...")
      }).catch(error => {
        console.error(error)
      });
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890;
    }
  }
}

</script>

<style scoped>
.mdi-close:hover {
  cursor: pointer;
}
</style>

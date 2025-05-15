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
            <v-tab value="one" :class="{ inactive: tab != 'one' }">Single</v-tab>
            <v-tab value="two" :class="{ inactive: tab != 'two' }">Multiple</v-tab>
            <v-tab value="three" :class="{ inactive: tab != 'three' }">Matrix</v-tab>
        </v-tabs>

        <v-window v-model="tab">
            <!-- SINGLE RACE -->
            <v-window-item value="one">
                <v-form class="mt-3" ref="singleForm" @submit.prevent="onSubmitSingle" lazy-validation>
                    <v-chip-group filter color="blue" v-model="selectedYearShortCutOptions">
                        <v-chip v-for="yearShortCut in yearShortCutOptions" v-if="yearShortCutOptions">{{ yearShortCut
                            }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Years -->
                    <v-container class="pa-0 d-flex pt-3">
                        <v-col cols="6" class="pa-0 pr-2">
                            <v-select clearable label="Von" :items="optionsYear" variant="outlined" v-model="startYear"
                                density="comfortable"
                                :rules="[v => !!v || 'Wähle ein Jahr als Anfangswert',
                                (v) => parseInt(v) <= parseInt(endYear) || 'Zeitraum Anfang darf nicht nach dem Ende liegen.']"></v-select>
                        </v-col>
                        <v-col cols="6" class="pa-0 pl-2">
                            <v-select clearable label="Bis" :items="optionsYear" v-model="endYear" variant="outlined"
                                density="comfortable"
                                :rules="[v => !!v || 'Wähle ein Jahr als Endwert',
                                (v) => parseInt(v) >= parseInt(startYear) || 'Zeitraum Ende darf nicht vor dem Anfang liegen.']"></v-select>
                        </v-col>
                    </v-container>

                    <!-- Gender-->
                    <v-chip-group multiple color="blue" v-model="selectedGenders">
                        <v-chip v-for="genderType in optionsGender">{{ genderType.charAt(0).toUpperCase() +
                            genderType.slice(1) }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Age Group -->
                    <v-chip-group multiple color="blue" v-model="selectedAges">
                        <v-chip v-for="ageGroup in optionsAges">{{ ageGroup.charAt(0).toUpperCase() + ageGroup.slice(1)
                            }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Bootsklasse-->
                    <v-select class="pt-3" density="comfortable" label="Bootsklasse" :items="optionsBoatClass"
                        v-model="selectedBoatClass" variant="outlined"></v-select>

                    <v-select class="pt-3" chips multiple density="comfortable" label="Event(s)"
                        :items="optionsCompTypes" v-model="selectedCompTypes" variant="outlined"
                        :rules="[v => v.length > 0 || 'Wähle mindestens eine Wettkampfklasse']">
                        <template v-slot:append-item>
                            <v-divider class="mt-2"></v-divider>
                            <v-list-item :title="competitionToggleText" @click="toggleSecondaryCompetitions()">
                                <template v-slot:prepend>
                                    <v-icon :icon="showMore ? 'mdi-chevron-down' : 'mdi-chevron-up'">
                                    </v-icon>
                                </template>
                            </v-list-item>
                        </template>

                    </v-select>

                    <v-chip-group class="pt-2" filter color="blue" multiple v-model="selectedRuns">
                        <v-chip density="comfortable" v-for="runOption in optionsRuns">
                            {{ runOption.charAt(0).toUpperCase() + runOption.slice(1) }}
                        </v-chip>
                    </v-chip-group>

                    <v-select label="Lauf" class="pt-2" clearable :items="optionsRunsFineSelection"
                        v-model="selectedRunsFineSelection" multiple variant="outlined" chips
                        :rules="[v => v.length > 0 || 'Wähle mindestens eine Laufkategorie']">
                    </v-select>





                    <v-label class="pt-1">Platzierung (optional)</v-label>
                    <v-chip-group filter color="blue" multiple v-model="selectedRanks">
                        <v-chip v-for="rank in optionsRanks">{{ rank }}</v-chip>
                    </v-chip-group>

                    <v-container class="pa-0 pt-4 text-right">
                        <v-btn color="grey" class="mx-2" @click="clearFormInputs">
                            <v-icon>mdi-backspace-outline</v-icon>
                        </v-btn>
                        <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
                    </v-container>


                </v-form>
            </v-window-item>

            <!-- MULIPLE RACES -->
            <v-window-item value="two">
                <v-form class="mt-3" ref="multipleForm" @submit.prevent="onSubmitMultiple" lazy-validation>
                    <v-chip-group filter color="blue" v-model="selectedYearShortCutOptions">
                        <v-chip v-for="yearShortCut in yearShortCutOptions" v-if="yearShortCutOptions">{{ yearShortCut
                            }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Years -->
                    <v-container class="pa-0 d-flex pt-3">
                        <v-col cols="6" class="pa-0 pr-2">
                            <v-select clearable label="Von" :items="optionsYear" variant="outlined" v-model="startYear"
                                density="comfortable"
                                :rules="[v => !!v || 'Wähle ein Jahr als Anfangswert',
                                (v) => parseInt(v) <= parseInt(endYear) || 'Zeitraum Anfang darf nicht nach dem Ende liegen.']"></v-select>
                        </v-col>
                        <v-col cols="6" class="pa-0 pl-2">
                            <v-select clearable label="Bis" :items="optionsYear" v-model="endYear" variant="outlined"
                                density="comfortable"
                                :rules="[v => !!v || 'Wähle ein Jahr als Endwert',
                                (v) => parseInt(v) >= parseInt(startYear) || 'Zeitraum Ende darf nicht vor dem Anfang liegen.']"></v-select>
                        </v-col>
                    </v-container>

                    <!-- Gender-->
                    <v-chip-group multiple color="blue" v-model="selectedGenders">
                        <v-chip v-for="genderType in optionsGender">{{ genderType.charAt(0).toUpperCase() +
                            genderType.slice(1) }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Age Group -->
                    <v-chip-group multiple color="blue" v-model="selectedAges">
                        <v-chip v-for="ageGroup in optionsAges">{{ ageGroup.charAt(0).toUpperCase() + ageGroup.slice(1)
                            }}
                        </v-chip>
                    </v-chip-group>

                    <!-- Bootsklasse-->
                    <v-select class="pt-3" multiple density="comfortable" label="Bootsklasse" :items="optionsBoatClass"
                        v-model="multipleBoatClass" variant="outlined">

                        <template v-slot:prepend-item>
                            <v-list-item title="Select All" @click="toggleSelectAll()">
                                <template v-slot:prepend>
                                    <v-checkbox-btn
                                        :indeterminate="(multipleBoatClass.length != 0 && !allSelected) || (allSelected && multipleBoatClass.length != optionsBoatClass.length) "
                                        :model-value="allSelected"></v-checkbox-btn>
                                </template>
                            </v-list-item>
                            <v-divider class="mt-2"></v-divider>
                        </template>


                    </v-select>

                    <v-select class="pt-3" chips multiple density="comfortable" label="Event(s)"
                        :items="optionsCompTypes" v-model="selectedCompTypes" variant="outlined"
                        :rules="[v => v.length > 0 || 'Wähle mindestens eine Wettkampfklasse']">
                        <template v-slot:append-item>
                            <v-divider class="mt-2"></v-divider>
                            <v-list-item :title="competitionToggleText" @click="toggleSecondaryCompetitions()">
                                <template v-slot:prepend>
                                    <v-icon :icon="showMore ? 'mdi-chevron-down' : 'mdi-chevron-up'">
                                    </v-icon>
                                </template>
                            </v-list-item>
                        </template>

                    </v-select>

                    <v-chip-group class="pt-2" filter color="blue" multiple v-model="selectedRuns">
                        <v-chip density="comfortable" v-for="runOption in optionsRuns">
                            {{ runOption.charAt(0).toUpperCase() + runOption.slice(1) }}
                        </v-chip>
                    </v-chip-group>

                    <v-select label="Lauf" class="pt-2" clearable :items="optionsRunsFineSelection"
                        v-model="selectedRunsFineSelection" multiple variant="outlined" chips
                        :rules="[v => v.length > 0 || 'Wähle mindestens eine Laufkategorie']">
                    </v-select>

                    <v-label class="pt-1">Platzierung (optional)</v-label>
                    <v-chip-group filter color="blue" multiple v-model="selectedRanks">
                        <v-chip v-for="rank in optionsRanks">{{ rank }}</v-chip>
                    </v-chip-group>

                    <v-container class="pa-0 pt-4 text-right">
                        <v-btn color="grey" class="mx-2" @click="clearFormInputs">
                            <v-icon>mdi-backspace-outline</v-icon>
                        </v-btn>
                        <v-btn color="blue" class="mx-2" type="submit">Übernehmen</v-btn>
                    </v-container>


                </v-form>
            </v-window-item>

            <!-- Matrix RACES -->
            <v-window-item value="three">
                <!-- year -->
                <v-select class="pt-4" clearable density="comfortable" label="Jahr" :items="optionsYear"
                    v-model="matrixYear" variant="outlined" :rules="[v => !!v || 'Wähle ein Jahr']">
                </v-select>

                <!-- Competitions -->
                <v-select class="pt-3" density="comfortable" label="Event" :items="optionsCompTypes"
                    v-model="matrixCompetition" variant="outlined">
                    <template v-slot:append-item>
                        <v-divider class="mt-2"></v-divider>
                        <v-list-item :title="competitionToggleText" @click="toggleSecondaryCompetitions()">
                            <template v-slot:prepend>
                                <v-icon :icon="showMore ? 'mdi-chevron-down' : 'mdi-chevron-up'">
                                </v-icon>
                            </template>
                        </v-list-item>
                    </template>
                </v-select>

                <!-- Gender -->
                <v-chip-group multiple color="blue" v-model="selectedGenders">
                    <v-chip v-for="genderType in optionsGender">{{ genderType.charAt(0).toUpperCase() +
                        genderType.slice(1) }}
                    </v-chip>
                </v-chip-group>

                <!-- Age Group -->
                <v-chip-group multiple color="blue" v-model="selectedAges">
                    <v-chip v-for="ageGroup in optionsAges">{{ ageGroup.charAt(0).toUpperCase() + ageGroup.slice(1)
                        }}
                    </v-chip>
                </v-chip-group>

                <!-- Bootsklasse -->
                <v-select class="pt-3" density="comfortable" label="Bootsklasse" :items="optionsBoatClass"
                    v-model="selectedBoatClass" variant="outlined"></v-select>

                <v-container class="pt-6 pa-0 pb-100 mb-100 text-right">
                    <v-btn color="blue" class="mx-2">Bestätigen</v-btn>
                </v-container>


            </v-window-item>
        </v-window>
    </v-container>

</template>


<script>
import Checkbox from "@/components/filters/checkbox.vue";
import { mapState } from "pinia";
import { useBerichteState } from "@/stores/berichteStore";


export default {
    components: { Checkbox },
    computed: {
        ...mapState(useBerichteState, {
            showFilter: "getFilterState",
            reportFilterOptions: "getReportFilterOptions"
        }),

    },
    data() {
        return {
            tab: "one",

            // year
            startYear: 0,
            endYear: 0,
            matrixYear: 0,
            optionsYear: [],
            yearShortCutOptions: [],
            selectedYearShortCutOptions: [],

            //Gender
            optionsGender: [],
            selectedGenders: [0],

            //Age Group
            optionsAges: [],
            selectedAges: [2],

            //Boat class
            optionsBoatClass: [],
            selectedBoatClass: "M1x",
            multipleBoatClass: ['M1x'],
            allSelected: false,

            // competition type
            compTypes: [], // list of dicts with objects containing displayName, id and key
            optionsCompTypes: [],
            selectedCompTypes: ["WCH", "OG", "WCp 1", "WCp 2", "WCp 3", "JWCH", "U23WCH"],
            matrixCompetition: "WCH",
            secondaryCompetitions: [],
            showMore: true,
            competitionToggleText: "Zeige mehr",

            // runs
            optionsRuns: [],
            selectedRuns: [0, 1, 2],
            optionsRunsFineSelection: [],
            selectedRunsFineSelection: [
                "fa",
                "fb",
                "fc",
                "fd",
                "sa/b",
                "sc/d",
                "q1-4"
            ],
            // ranks
            optionsRanks: [],
            selectedRanks: []
        }

    },
    created() {
        window.addEventListener('resize', this.checkScreen)
        this.checkScreen();

        const store = useBerichteState();
        const setFilterValues = async () => {
            await store.fetchReportFilterOptions()
            const data = this.reportFilterOptions[0]

            //Years
            this.startYear = data.years[0].start_year
            this.endYear = data.years[1].end_year
            this.matrixYear = data.years[0].start_year
            this.yearShortCutOptions = [`Gesamter Zeitraum`, "Aktuelles Jahr", "Aktueller OZ", "Letzter OZ"]
            this.optionsYear = Array.from({length: this.endYear - this.startYear + 1}, (_, i) => this.endYear - i)
            this.selectedYearShortCutOptions = [0]

            //Gender
            this.optionsGender = Object.keys(data.boat_classes)
            this.optionsGender.pop() //Remove the all option

            //Age
            this.optionsAges = Object.keys(data.boat_classes.m)

            //Boat class
            this.updateBoatClass()

            //competitions
            this.compTypes = data.competition_categories
            this.optionsCompTypes = this.compTypes.map(item => item.display_name)
            this.secondaryCompetitions = data.secondary_competition_categories?.map(item => item.display_name) || [];

            // runs
            this.runsData = data.runs
            this.optionsRuns = Object.keys(data.runs)
            const tempObj = Object.values(data.runs)
            this.optionsRunsFineSelection = tempObj.reduce((acc, obj) => obj ? acc.concat(Object.keys(obj)) : acc, []);

            // ranks
            this.optionsRanks = data.ranks

        }
        setFilterValues()

    },
    methods: {
        checkScreen() {
            this.windowWidth = window.innerWidth;
            this.mobile = this.windowWidth < 890;
        },
        hideFilter() {
            const store = useBerichteState()
            store.setFilterState(this.showFilter)
        },
        clearFormInputs() {
            this.selectedGenders = [0]
            this.optionsAges = [],
            this.selectedBoatClass = "M1x",
            this.startYear = this.reportFilterOptions[0].years[0].start_year
            this.endYear = new Date().getFullYear()
            this.selectedCompTypes =  ["WCH", "OG", "WCp 1", "WCp 2", "WCp 3", "JWCH", "U23WCH"]
            this.selectedRanks = []
            this.selectedRuns = [0, 1, 2]
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
                //No Age Groups in mixed
                if (gender == "mixed") {
                    this.optionsBoatClass.push(...Object.values(this.reportFilterOptions[0].boat_classes[gender]).map(item => item[0]));
                continue;
                }
                //Age Group
                for (const age of selectedAgesValue) {
                //Category
                for(const category in this.reportFilterOptions[0].boat_classes[gender][age]) {
                    const boatClass = this.reportFilterOptions[0].boat_classes[gender][age][category][0]
                    this.optionsBoatClass.push(boatClass)
                }
                }
            }
        },
        toggleSecondaryCompetitions() {
            this.optionsCompTypes = this.showMore
            ? [...this.optionsCompTypes, ...this.secondaryCompetitions] // Hinzufügen
            : this.optionsCompTypes.filter(comp => !this.secondaryCompetitions.includes(comp)); // Entfernen

            this.showMore = !this.showMore
            this.competitionToggleText = this.showMore ? "Zeige mehr" : "Zeige weniger";
        },
        toggleSelectAll() {
            if (this.allSelected) {
                this.multipleBoatClass = [];
            } else {
                this.multipleBoatClass = [...this.optionsBoatClass];
            }
            this.allSelected = !this.allSelected;
        },
        async onSubmitSingle() {
            const { valid } = await this.$refs.singleForm.validate()
            if (valid) {
                this.hideFilter()
                this.submitSingle()
            } else {
                alert("Bitte überprüfen Sie die Eingaben.")
            }
        },
        async onSubmitMultiple() {
            const { valid } = await this.$refs.multipleForm.validate()
            if (valid) {
                this.hideFilter()
                this.submitMultiple()
            } else {
                alert("Bitte überprüfen Sie die Eingaben.")
            }
        },
        submitSingle() {
            const formData = this.buildFormData(this.selectedBoatClass);

            const store = useBerichteState()
            store.postFormData(formData)
                .then(() => {console.log("data sent...")})
                .catch(error => {console.error(error)})

            store.setLastFilterConfig(this.buildFilterConfig(formData));
        },
        submitMultiple() {
            const formData = this.buildFormData(this.multipleBoatClass);
            const store = useBerichteState()
            store.postFormDataMatrix(formData)
                .then(() => {console.log("data sent...")})
                .catch(error => {console.error(error)})
                
            store.setLastFilterConfig(this.buildFilterConfig(formData));

        },
        getRacePhaseSubtypes(selectedKeys, runsData) {
            // find run keys for race_phase_subtype
            // TODO: This makes no sense, no difference between phases
            return selectedKeys.reduce((acc, key) => {
                const value = Object.values(runsData).find(obj => obj.hasOwnProperty(key));
                if (value && Array.isArray(value[key])) {
                    return acc.concat(value[key]);
                } else if (value) {
                    return acc.concat(value[key]);
                } else {
                    return acc;
                }
            }, []);
        },
        buildFormData(boatClass) {
            const racePhaseSubtypes = this.getRacePhaseSubtypes(this.selectedRunsFineSelection, this.runsData);

            const formData = {
                interval: [this.startYear, this.endYear],
                competition_type: this.compTypes
                    .filter(item => this.selectedCompTypes.includes(item.display_name))
                    .map(item => item.id),
                boat_class: boatClass,
                race_phase_type: this.selectedRuns.map(item => this.optionsRuns[item]),
                race_phase_subtype: [...new Set(racePhaseSubtypes)],
            };

            const placement = this.selectedRanks.map(item => this.optionsRanks[item]);
            if (placement.length > 0) {
                formData.placement = placement;
            }

            return formData;
        },
        buildFilterConfig(formData) {
            return {
                ...formData,
                competition_type: this.selectedCompTypes.join(", "),
                race_phase_type: this.selectedRuns.map(item => this.optionsRuns[item]).join(", "),
                race_phase_subtype: this.selectedRunsFineSelection.join(", "),
                placement: this.selectedRanks.map(item => this.optionsRanks[item]).join(", ")
            };
        }


    },
    watch: {
        selectedGenders: function () {
            this.updateBoatClass()
        },
        selectedAges: function () {
            this.updateBoatClass()
        },
        selectedRuns: function (newVal,) {
            if (newVal !== undefined && this.reportFilterOptions !== undefined) {
                const newSelection = Object.values(newVal)
                let newFineSelectionEntries = newSelection.reduce((acc, idx) => {
                    const obj = Object.values(this.runsData)[idx] ?? {};
                    return acc.concat(Object.keys(obj));
                }, []);
                this.selectedRunsFineSelection = newFineSelectionEntries
                this.optionsRunsFineSelection = newFineSelectionEntries
            }
        },
        selectedYearShortCutOptions: function (newVal) {
            const currentYear = new Date().getFullYear();
            if (newVal === 0) {
                this.startYear = this.reportFilterOptions[0].years[0].start_year;
                this.endYear = this.reportFilterOptions[0].years[1].end_year;
            } else if (newVal === 1) {
                this.startYear = currentYear;
                this.endYear = currentYear;
            } else if (newVal === 2 || newVal === 3) {
                const olympicYear = currentYear - (currentYear % 4) + 4;
                if (newVal === 2) {
                    if (currentYear >= 2022 && currentYear <= 2024) {
                        this.startYear = 2022;
                        this.endYear = 2024;
                    } else if (currentYear >= 2025 && currentYear <= 2028) {
                        this.startYear = 2025;
                        this.endYear = 2028;
                    } else {
                        this.startYear = olympicYear - 3;
                        this.endYear = olympicYear - 1;
                    }
                }
                else {
                    if (currentYear >= 2022 && currentYear <= 2024) {
                        this.startYear = 2017;
                        this.endYear = 2021;
                    } else if (currentYear >= 2025 && currentYear <= 2028) {
                        this.startYear = 2022;
                        this.endYear = 2024
                    } else {
                        this.startYear = olympicYear - 7;
                        this.endYear = olympicYear - 3;
                    }
                }
            }
        },
    }
}

</script>

<style scoped>
.mdi-close:hover {
    cursor: pointer;
}

.inactive {
    background-color: #EEEEEE;
    border-left: 1px solid darkgrey;
    border-right: 1px solid darkgrey;
    color: #000;
}
</style>
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
                <rennstruktur-filter/>
            </v-navigation-drawer>

            <!-- Main Content-->
            <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
                <!-- Heading "Rennstrukturanalyse" + icon options -->
                <v-col cols="6" class="d-flex flex-row px-0" style="align-items: center"
                    v-bind:style='{ "padding-top": windowWidth < 400 ? "18px" : "12px" }, { "padding-bottom": (windowWidth < 400 ? "18px" : "12px") }'>
                    <h1 v-bind:style='{ "font-size": (windowWidth < 400 ? "22px" : "30px") }'>Rennstrukturanalyse</h1>
                    <v-icon id="tooltip-analysis-icon" color="grey"
                        class="ml-2 v-icon--size-large">mdi-information-outline
                    </v-icon>
                    <v-tooltip activator="#tooltip-analysis-icon" location="end" open-on-hover>Die Rennstrukturanalyse
                        erlaubt die Betrachtung des Rennverlaufes
                        ein oder mehrerer Rennen basierend auf Ergebnis- und GPS-Daten.
                    </v-tooltip>
                    <!-- FIX EMAIL -->
                    <a>
                        <v-icon color="grey" class="ml-2 v-icon--size-large">mdi-email-outline
                        </v-icon>
                    </a>
                    <v-icon @click="openPrintDialog()" color="grey" class="ml-2 v-icon--size-large">mdi-printer</v-icon>
                    <v-icon @click="exportTableData()" color="grey" class="ml-2 v-icon--size-large"
                        v-if="display == 'SINGLE'">mdi-table-arrow-right
                    </v-icon>
                    <v-icon @click="exportRaces()" color="grey" class="ml-2 v-icon--size-large"
                        v-if="display == 'MULTIPLE'">mdi-table-arrow-right
                    </v-icon>
                </v-col>
                <v-divider></v-divider>

                <!--LOADING-->
                <v-progress-circular v-if="loading" class="pa-0 mt-3" indeterminate color="blue"
                    size="40"></v-progress-circular>

                <!--Show Views -->
                <router-view v-if="!loading"/>


            </v-container>

        </v-layout>
    </v-card>

</template>

<script setup>
import RennstrukturFilter from "@/components/filters/rennstrukturFilter.vue";
import '@/assets/base.css';
import 'chartjs-adapter-moment';

</script>

<script>
import { useRennstrukturAnalyseState } from "@/stores/baseStore";
import { mapState } from "pinia";
import { useGlobalState } from "@/stores/globalStore";

export default {
    computed: {
        ...mapState(useGlobalState, {
            headerReduced: "getHeaderReducedState"
        }),

        ...mapState(useRennstrukturAnalyseState, {
            loading: "getLoadingState",
            filterState: "getFilterState",
            display: "getDisplay"
        }),
    },

    data() {
        return {
            filterOpen: false,
            mobile: false,

        }
    },
    created() {
        window.addEventListener('resize', this.checkScreen);
        this.checkScreen();
        this.filterOpen = this.filterState

    },
    methods: {
        setFilterState() {
            this.filterOpen = !this.filterOpen;
            const store = useRennstrukturAnalyseState()
            store.setFilterState(this.filterState)
        },
        checkScreen() {
            this.windowWidth = window.innerWidth;
            this.mobile = this.windowWidth < 890
            let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
            document.documentElement.style.setProperty('--navbar-height', navbarHeight);
        },
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
        }
    }
}

</script>

<style lang="scss" scoped>

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
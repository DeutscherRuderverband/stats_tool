<template>
  <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
    <v-col cols="12" class="px-0">
      <h1>Kalender</h1>
    </v-col>
    <v-divider></v-divider>
    <v-row class="ma-0" style="display: flex; justify-content: space-between; align-items: flex-end;">
      <v-chip-group filter color="blue" v-model="selectedView">
        <v-chip>Monat</v-chip>
        <v-chip>Jahr</v-chip>
      </v-chip-group>
      <v-list class="d-flex pa-2 ma-1 mx-0" style="background-color: #f7f4f4; border-radius: 3px">
        <div :style="{'display': 'grid', 'grid-template-columns': (mobile ? 'repeat(2, 1fr)' : 'repeat(4, 2fr)')}">
          <v-list-item v-for="(value, key) of legend" :key="key" class="d-flex px-1 py-0" min-height="0" style="font-size: 11px">
            <div class="d-flex align-center pa-0">
              <div :style="{ backgroundColor: value, width: '15px', height: '15px', borderRadius: '2px' }"></div>
              <p style="display: inline-block; padding-left: 5px;">{{ key }}</p>
            </div>
          </v-list-item>
        </div>
      </v-list>
    </v-row>
    <div class="text-center section">
      <v-calendar
        class="custom-calendar"
          :masks="masks"
          :attributes="attributes"
          disable-page-swipe
          is-expanded
          :style="{'border-radius': '0'}"
          :rows="selectedView ? (mobile ? 12 : 3) : 1"
          :columns="selectedView ? (mobile ? 1 : 4) : 1"
          ref="calendar"
      >
        <template v-slot:day-content="{ day, attributes }">
          <div class="h-full z-10" style="min-height: 60px; display: flex; flex-direction: column;">
            <span class="day-label text-sm">{{ day.day }}</span>
            <div>
                <div v-for="attr in attributes" class="rounded-sm my-1"
                    :key="attr.key" :style=attr.customData.style>
                  <router-link style="color: white; display: flex; flex-direction: column;"
                    :to="`/rennstrukturanalyse?comp_id=${attr.key}`">
                    <p class="leading-tight pa-1"
                      :style="{
                        wordWrap: 'break-word', display: 'inline-block',
                        lineHeight: 'normal', maxWidth: mobile ? '45px' : '120px', fontSize: mobile ? '11px' : '14px'
                      }"
                    >
                      {{ selectedView ? "" : attr.customData.title }}
                    </p>
                  </router-link>
                </div>
              </div>
            </div>
        </template>
      </v-calendar>
    </div>
  </v-container>
</template>

<script>
import {mapState} from "pinia";
import {useHomeStore} from "@/stores/homeStore";

export default {
  computed: {
    ...mapState(useHomeStore, {
      calenderData: "getCalenderData"
    }),
    ...mapState(useHomeStore, {
      legend: "getCalenderLegend"
    }),
  },
  data() {
    return {
      mobile: false,
      opacity: 0.65,
      masks: {
        weekdays: 'WWW',
      },
      attributes: [],
      selectedView: 0
    };
  },
  mounted() {
    this.$watch(
      () => this.$refs.calendar.firstPage.year,
      (newYear, ) => {
        const store = useHomeStore()
        store.fetchCalendarData(newYear)
      }
    )
  },
  created() {
    this.attributes = this.calenderData
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();

    const store = useHomeStore()
    store.fetchCalendarData(new Date().getFullYear())
  },
  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  watch: {
    calenderData(newVal) {
      this.attributes = newVal
    }
  }
};
</script>

<style scoped>
.main-container {
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}
</style>
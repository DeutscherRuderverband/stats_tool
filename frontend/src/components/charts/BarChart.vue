<script setup>
import {Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { Bar } from 'vue-chartjs'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
</script>

<template>
  <div class="chart-container" :style="{ minHeight: mobile ? '200px' : '380px' }">
    <Bar
      :options="chartOptions"
      :data="data"
    />
  </div>
</template>

<script>
export default {
  props: ['data', 'chartOptions'],
  data() {
    return {
      mobile: false
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },
  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
    }
  }
}
</script>

<style lang="scss" scoped>
@media print {
  canvas {
    min-height: 100%;
    max-width: 100%;
    max-height: 100%;
    height: auto!important;
    width: auto!important;
  }

  .chart-container {
    min-height: 0 !important;
  }
}
</style>

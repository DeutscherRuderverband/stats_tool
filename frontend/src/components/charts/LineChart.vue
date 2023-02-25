<template>
    <div class="chart-container" :style="{ minHeight: mobile ? '200px' : '380px' }">
      <Line
        :options="chartOptions"
        :data="data"
      />
    </div>
</template>

<script>
import {Line} from "vue-chartjs";
import {Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend} from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default {
  name: 'App',
  components: {
    Line
  },
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

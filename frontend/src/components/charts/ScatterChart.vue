<template>
  <div class="chart-container" :style="{ minHeight: mobile ? '200px' : '380px' }">
    <scatter
      :options="chartOptions"
      :data="data"
    />
  </div>
</template>

<script>
import {Scatter} from "vue-chartjs";

export default {
  components: {
    Scatter
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

<style>
.chart-container {
  position: relative;
  margin: auto;
  height: 100%;
  width: 100%;
}
</style>

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
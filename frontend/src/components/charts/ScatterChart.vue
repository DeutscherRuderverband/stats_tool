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
      this.mobile = this.windowWidth <= 750
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
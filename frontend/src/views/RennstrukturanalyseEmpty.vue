<template>

    <v-container class="pa-0 mt-3">
        <v-alert type="info" variant="tonal" :width="mobile ? '100%' : '50%'">
            Bitte wähle ein Jahr und ein Event in dem Filter auf der linken Seite.
        </v-alert>
    </v-container>

</template>


<script>

export default {
  data() {
    return {
      mobile: false,
    }
  },
  created() {
    window.addEventListener('resize', this.checkScreen);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateWidth)
  },
  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
    },
  }
}

</script>
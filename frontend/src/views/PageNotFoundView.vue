<template>
  <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
    <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
      <h1>Seite nicht gefunden</h1>
    </v-col>
    <v-divider></v-divider>
    <v-container class="pa-0 mt-2" style="min-height: 450px">
      <v-col class="pl-0 pr-0">
      <p>Die gesuchte Seite konnte nicht gefunden werden. Sie wurde möglicherweise entfernt, umbenannt oder existierte von vornherein nicht.</p>
      <br />
      <RouterLink to="/"><v-btn color="#2a9af3" style="color: white; font-weight: bold;">Zurück zur Startseite</v-btn></RouterLink>
      </v-col>
    </v-container>
  </v-container>
</template>

<script>
export default {
  created(){
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
    window.scrollTo(0, 0)
  },
  methods: {
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth < 890
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  data() {
    return {
      mobile: false,
    }
  }
}
</script>

<style lang="scss" scoped>
.main-container {
  min-height: calc(100vh - (var(--navbar-height)) - 94px);
}
</style>
<template>
  <footer class="footer" :style="mobile ? 'min-height: 99px' : 'min-height: 94px;'">
    <v-container :class="mobile ? 'px-5 pt-2 pb-1 d-sm-flex' : 'px-10 pt-6 d-sm-flex flex-justify-between flex-items-center'">
      <RouterLink to="/impressum" :class="mobile ? (minreached ? 'ml-2' : 'mt-3 ml-6 mr-3' ) : 'mt-3 mr-3'">Impressum</RouterLink>
      <RouterLink to="/datenschutz" :class="minreached ? 'ml-2' : 'ma-3'">Datenschutz</RouterLink>
      <RouterLink to="/hilfe" :class="minreached ? 'ml-2' : 'ma-3'">Hilfe</RouterLink>
      <RouterLink to="/mitwirkende" :class="minreached ? 'ml-2' : 'ma-3'">Mitwirkende</RouterLink>
      <v-spacer class="my-2"></v-spacer>
        <a href="https://ai.hdm-stuttgart.de/" class="mr-6"><img src="@/assets/images/IAAI_Logo_white.svg" :width="minreached ? 55 : 69"></a>
        <a href="https://www.hdm-stuttgart.de/" :class="mobile ? (minreached ? 'mr-0' : 'mr-5') :'mr-0'"><img src="@/assets/images/HDM_Logo_white.svg" :width="minreached ? 45 : 54"></a>
      </v-container>
  </footer>
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
      this.mobile = this.windowWidth < 890;
      this.minreached = this.windowWidth < 600;
      let navbarHeight = window.innerWidth < 890 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  },
  data() {
    return {
      mobile: false,
      minreached: false
    }
  }
}
</script>

<style lang="scss" scoped>
.footer {
  text-align: center;
  font-style: italic;
  align-items: center;
  display: flex;
  margin: 0 auto;
  left: 0;
  right: 0;
  width: 100%;
  background-color: #1369b0;
  justify-self: center;
  bottom: 0;
}

a {
  color: rgba(255,255,255,0.75);
}

a:hover {
  color: white;
}
</style>
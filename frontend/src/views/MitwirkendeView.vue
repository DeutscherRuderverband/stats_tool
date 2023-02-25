<template>
  <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
    <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
      <h1>Mitwirkende</h1>
    </v-col>
    <v-divider></v-divider>
    <v-container class="pa-0 mt-2" style="min-height: 450px">
      <v-row class="mt-2 mb-2" style="min-height: 450px">
      <v-col :cols="mobile ? 12 : 6">
        <h2>UI/UX</h2>
        <p>Anke Müller</p>
        <br>
        <h2>Frontend</h2>
        <p>Harri Faßbender<br />
          Julian Fritzmann</p>
        <br>
        <h2>Backend</h2>
        <p>Nicolas Reinhart<br />
          Raphael Wettinger<br />
          Harri Faßbender</p>
        <br>
        <h2>Betreuer</h2>
        <p>Prof. Dr.-Ing. Johannes Maucher</p>
        <br>
        <h2>DRV-Vertreter</h2>
        <p>Dr. Kay Winkert<br />
          Markus Last</p>
      </v-col>
      <v-col :cols="mobile ? 12 : 6">
        <h2>Entwicklung</h2>
        <p>Diese Webanwendung wurde im Wintersemester 2022/2023 von Studierenden des Masterstudiengangs Computer Science and Media am Institute for Applied Artificial Intelligence (IAAI) an der Hochschule der Medien Stuttgart entwickelt.</p>
        <br>
        <a href="https://ai.hdm-stuttgart.de/" class="mr-5"><img src="@/assets/images/IAAI_Logo_black.svg" width="100"></a>
        <a href="https://www.hdm-stuttgart.de/"><img src="@/assets/images/HDM_Logo_color.svg" width="80"></a>
        <br>
        <br>
        <h2>Idee</h2>
        <p>Die Idee für diese Webanwendung stammt von Mitgliedern des Deutschen Ruderverbands. Sie wurde im engen Austausch mit den Enwicklern verfeinert und umgesetzt.</p>
        <br>
        <a href="https://www.rudern.de/"><img src="@/assets/images/DRV_Logo_large.svg" width="120"></a>
      </v-col>
      </v-row>
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
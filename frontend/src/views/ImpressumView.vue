<template>
  <v-container :class="mobile ? 'px-5 py-2 main-container' : 'px-10 pt-0 main-container'">
    <v-col cols="12" class="d-flex flex-row px-0" style="align-items: center">
      <h1>Impressum</h1>
    </v-col>
    <v-divider></v-divider>
    <v-container class="pa-0 mt-2" style="min-height: 450px">
      <v-col class="pl-0 pr-0">
      <h2><i>Herausgeber:</i></h2>
      <p>Deutscher Ruderverband<br />
        Markus Last<br />
        Ferdinand-Wilhelm-Fricke-Weg 10<br />
        30169 Hannover<br />
        Telefon: +49 (0) 4541 8643 46<br />
        E-Mail: <a href="mailto:markus.last@rudern.de">markus.last@rudern.de</a></p>
      <br>
      <h2>Rechtliche Hinweise</h2>
      <p>Wichtiger Hinweis zu allen Links. Wir sind nicht für die Inhalte fremder Seiten verantwortlich, die über einen
      Link erreicht werden. Diese Erklärung gilt für alle auf <a href="https://drv-stats.up.railway.app/">https://drv-stats.up.railway.app/</a> angebrachten Links.</p>
      <br>
      <h2>Haftungsausschluss</h2>
      <p>Die auf diesen Websites bereitgestellten Informationen wurden geprüft und werden regelmäßig aktualisiert. Es kann
      jedoch keine Garantie dafür übernommen werden, dass alle Angaben zu jeder Zeit vollständig, richtig und in letzter
      Aktualität dargestellt sind. Dies gilt insbesondere für alle Links zu anderen Websites, auf die direkt oder
      indirekt verwiesen wird. Alle Angaben können ohne vorherige Ankündigung ergänzt, entfernt oder geändert werden.</p>
      <br>
      <h2>Urheberrecht</h2>
      <p>Die auf <a href="https://drv-stats.up.railway.app/">https://drv-stats.up.railway.app/</a> veröffentlichen Informationen stammen aus öffentlich zugänglichen
      Wettkampf- und Ergebnisinformationen. Für die Verwendung von dem aufgearbeiteten Text- oder Bildmaterial bedarf es
      dennoch der vorherigen Zustimmung durch den Seitenbetreiber.</p>
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
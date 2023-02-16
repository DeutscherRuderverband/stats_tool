<template>
  <footer class="footer">
    <v-container>
      <RouterLink to="/impressum" style="color: white" class="pa-2">Impressum</RouterLink>
      <RouterLink to="/datenschutz" style="color: white" class="pa-2">Datenschutz</RouterLink>
      <RouterLink to="/hilfe" style="color: white" class="pa-2">Hilfe</RouterLink>
    </v-container>
  </footer>
</template>


<style lang="scss" scoped>
.footer {
  text-align: center;
  font-style: italic;
  margin: auto;
  left: 0;
  right: 0;
  width: 100%;
  background-color: #1369b0;
  justify-self: center;
  min-height: 100px;
  bottom: 0;
}
</style>
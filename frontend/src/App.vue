<template>
  <Navigation />
  <RouterView />
  <FooterC />
</template>


<script setup>
import { RouterView } from 'vue-router'
import Navigation from './components/Navigation.vue'
import FooterC from './components/Footer.vue';
</script>

<style lang="scss" scoped>
.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

body {
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding-left: 2em;
  padding-right: 2em;
}
</style>

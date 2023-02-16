<template>
  <v-container :class="mobile ? 'px-5 main-container' : 'px-10 pt-0 main-container'">
    <v-col cols="12" class="pa-0 pt-0" justify="center">
      <h1 class="py-3">Login</h1>
      <v-col cols="6" class="px-0">
        <v-alert type="info" variant="tonal">
          Diese Seite ist passwortgeschützt. Bitte melde dich an um fortzufahren.
        </v-alert>
      </v-col>
      <v-col cols="12" sm="8" md="4" class="px-0">
        <v-form class="px-0" @submit.prevent="login">
          <v-text-field
              label="Nutzername"
              v-model="username"
              variant="outlined"
              density="compact"></v-text-field>
          <v-text-field
              label="Passwort"
              type="password"
              v-model="password"
              variant="outlined"
              density="compact"></v-text-field>
          <v-btn color="#1369b0" style="color: white" type="submit">Login</v-btn>
        </v-form>
      </v-col>
    </v-col>
  </v-container>
</template>

<script>
import axios from 'axios';
import router from '../router'

export default {
  data() {
    return {
      username: 'drv_test_user',
      password: ''
    }
  },
  created() {
    this.attributes = this.calenderData
    window.addEventListener('resize', this.checkScreen);
    this.checkScreen();
  },
  methods: {
    async login() {
      try {
        const response = await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/login`, {
          user: this.username,
          pass: this.password
        });

        const token = response.data.access_token;
        localStorage.setItem('session_token', token)
        router.push('/');

      } catch (error) {
        console.log("Login failed. Wrong credentials.")
        console.log(error)
        /** TODO: render fail msg to DOM */
      }
    },
    checkScreen() {
      this.windowWidth = window.innerWidth;
      this.mobile = this.windowWidth <= 750
      let navbarHeight = window.innerWidth < 750 ? '71.25px' : '160px';
      document.documentElement.style.setProperty('--navbar-height', navbarHeight);
    }
  }
}
</script>

<style scoped>
.main-container {
  min-height: calc(100vh - (var(--navbar-height)) - 95px);
}
</style>

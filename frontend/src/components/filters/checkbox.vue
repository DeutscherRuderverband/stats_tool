<template>
  <v-list>
    <v-list-item class="pa-0" density="compact" v-for="item in checkboxDaten" :key="item.id">
      <v-checkbox
          v-model="item.selected"
          :label="item.name"
          hide-details
      />
    </v-list-item>
  </v-list>
</template>

<script>
export default {
   props: ['checkboxDaten'],
}
</script>

<style scoped>
.v-list-item--density-compact.v-list-item--one-line {
  min-height: 20px !important;
  height: 40px;
}
</style>
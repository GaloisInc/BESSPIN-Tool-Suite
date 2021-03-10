<template>
  <div id="app">
    <NGMap/>
    <CyberPhys/>
  </div>
</template>

<script>
import CyberPhys from './components/CyberPhys.vue'
import NGMap from './components/NGMap.vue'

export default {
  name: 'App',
  components: {
    CyberPhys,
    NGMap
  }
}
</script>

<style>
html, body, template, #app {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>

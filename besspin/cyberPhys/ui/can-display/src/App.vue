<template>
  <div id="app">
    <div id="can-legend">
      <table>
        <tr><th>CAN ID</th><th>Description</th></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
        <tr><td>AA123453</td><td>Some Description of subsystem</td></tr>
      </table>
    </div>
    <Console/>
  </div>
</template>

<script>
import Console from './components/Console.vue'

export default {
  name: 'App',
  components: {
    Console
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Staatliches&display=swap');
html, body {
    background-color: #222;
    overflow: hidden;
    background-image: url('/canBus_normal.png');
}
#ssith-status {
  width: 600px;
  position: absolute;
  top: 200px;
  left: 400px;
}
#console {
  position: absolute;
  top: 650px;
  left: 550px;
}
#can-legend {
  left: 124px;
  top: 380px;
  position: absolute;
}
#can-legend th {
  padding: 0;
  text-align: left;
  border-bottom: 3px solid;
}
#can-legend tr :first-child {
  border-right: 1px solid;
}
#can-legend td, #can-legend th {
    padding: 5px;
}
#can-legend table {
  border-collapse: collapse;
  border-spacing: 0;
}
h1 {
  font-size: 80px;
  text-align: center;
}
#app {
  font-family: 'Staatliches', cursive;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ddd;
  margin-top: 60px;
}
</style>

<template>
  <div id="app">
    <h1 id="title-status">All Systems Normal</h1>
    <div id="ssith-status">
      <h2>Status</h2>
      <h1>NO SSITH HARDWARE PROTECTION</h1>
    </div>
    <div id="can-legend">
      <h2>Can Bus Codes</h2>
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
}
#ssith-status {
  width: 600px;
  position: absolute;
  top: 200px;
  left: 400px;
}
#can-legend {
  float: left;
  margin-left: 30px;
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

<template>
  <div id="app" :class="[state]">
    <div id="can-legend">
      <table>
        <tr><th>CAN ID</th><th>Description</th></tr>
        <tr><td>AAF01000</td><td>Gear Selection</td></tr>
        <tr><td>AAF01A00</td><td>Throttle Input</td></tr>
        <tr><td>AAF01B00</td><td>Brake Input</td></tr>
        <tr><td>AAF01D00</td><td>Steering Angle</td></tr>
        <tr><td>AAFEAA00</td><td>Fuel remaining</td></tr>
      </table>
    </div>
    <Console/>
    <Debug/>
  </div>
</template>

<script>
import Console from './components/Console.vue'
import Debug from './components/Debug.vue'
const electron = require('electron')
const ipc = electron.ipcRenderer;

export default {
  name: 'App',
  components: {
    Console,
    Debug
  },
  data() {
    return {
      state: "normal",
      poller: setInterval(() => { this.pollState() }, 100)
    }
  },
  mounted() {
    ipc.on('zmq-results',(event, q) => {
      q.forEach(item => {
        if(this.state != item.retval) {
          this.state = item.retval;
        }
      });
    });
  },
  unmounted() {
    clearInterval(this.poller);
  },
  methods: {
    pollState() {
      ipc.send('zmq-poll', []);
    },
    changeState(state) {
      this.state = state;
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Staatliches&display=swap');
html, body {
    background-color: #222;
    overflow: hidden;
    margin: 0;
    padding: 0;
}
#ssith-status {
  width: 600px;
  position: absolute;
  top: 200px;
  left: 400px;
}
#debug {
  position: absolute;
  top: 870px;
  left: 120px;
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
#can-legend td {
  width: 140px;
  font-family: 'Roboto Mono', monospace;
}
#can-legend th {
  padding: 0;
  text-align: left;
  font-weight: bold;
}

#can-legend td, #can-legend th {
    padding: 2px;
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
  background-image: url('/canBus_normal.png');
  overflow: hidden;
  width: 100vw;
  height: 100vh;
}
#app.normal {
  background-image: url('/canBus_normal.png');
}
#app.hacked {
  background-image: url('/canBus_hacked.png');
}
#app.ssith {
  background-image: url('/canBus_protected.png');
}

</style>

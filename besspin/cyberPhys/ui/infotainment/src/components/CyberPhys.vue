<template>
  <div id="cyberphys">
    <button @click="selectChannel(1)" type="button" id="station1"  v-bind:class="{selected: activeChannel == 1}" class="station-button"></button>
    <button @click="selectChannel(2)" type="button" id="station2" v-bind:class="{selected: activeChannel == 2}" class="station-button"></button>
    <button @click="selectChannel(3)" type="button" id="station3" v-bind:class="{selected: activeChannel == 3}" class="station-button"></button>

    <button @click="incVolume()" type="button" id="vol-up" class="vol-button"></button>
    <button @click="decVolume()" type="button" id="vol-down" class="vol-button"></button>

    <button @click="resetSim()" type="button" id="reset-sim" class="reset-btn">Reset</button>
  </div>
</template>

<script>
const { ipcRenderer } = require('electron')

export default {
  name: 'CyberPhys',
  props: {
  },
  data: function() {
    return {
      activeChannel: 0
    }
  },
  mounted: function() {
  },
  methods: {
    resetSim: function() {
      console.log('Resetting simulator scenario');
      ipcRenderer.send('button-pressed', 'reset', {});
    },
    incVolume: function() {
      ipcRenderer.send('volume-inc');
    },
    decVolume: function() {
      ipcRenderer.send('volume-dec');
    },
    selectChannel: function(number) {
      ipcRenderer.send('channel-selected', number);
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.reset-btn {
  position: absolute;
  background: #F44336;
  color: #fff;
  font-weight: bold;
  font-size: 1.2em;
  border-radius: 40px;
  border: none;
  height: 45px;
  width: 100px;
  bottom: 70px;
  right: 50px;
}
.reset-btn:active, .reset-btn:focus {
  outline: none;
}
.reset-btn:active {
    background: #d2190b;
}
.vol-button, .station-button {
  position: absolute;
  background: none;
  border: 0;
  outline: none;
}
.station-button {
  left: 60px;
  height: 47px;
  width: 221px;
  background-size: 100%;
  background-repeat: none;
}
.vol-button {
  left: 72px;
  height: 52px;
  width: 210px;
  background-size: 100%;
  background-repeat: none;
}
#station1 {
  top: 76px;
  background-image: url('../assets/img/station1-dark.png');
}
#station1:active {
  background-image: url('../assets/img/station1-med.png');
}
#station1.selected {
  background-image: url('../assets/img/station1-light.png');
}
#station2 {
  top: 136px;
  background-image: url('../assets/img/station2-dark.png');
}
#station2:active {
  background-image: url('../assets/img/station2-med.png');
}
#station2.selected {
  background-image: url('../assets/img/station2-light.png');
}
#station3 {
  top: 196px;
  background-image: url('../assets/img/station3-dark.png');
}
#station3:active {
  background-image: url('../assets/img/station3-med.png');
}
#station3.selected {
  background-image: url('../assets/img/station3-light.png');
}
#vol-up {
  top: 302px;
  background-image: url('../assets/img/volume-up-dark.png');
}
#vol-up:active {
  background-image: url('../assets/img/volume-up-light.png');
}
#vol-down {
  top: 375px;
  background-image: url('../assets/img/volume-down-dark.png');
}
#vol-down:active {
    background-image: url('../assets/img/volume-down-light.png');
}
#cyberphys {
  height: 480px;
  width: 800px;
  background-image: url('../assets/img/infotainment-ui.png');
  background-size: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0;
}
</style>

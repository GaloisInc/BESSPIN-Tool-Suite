<template>
  <div>
    <div id="ngmap" v-bind:style="{ backgroundPosition: -x + 'px ' + y + 'px', transform: 'rotate(' + -r + 'deg)'}"></div>
    <div id="pointer"></div>
  </div>
</template>

<script>
const electron = require('electron')
const ipc = electron.ipcRenderer;
export default {
  name: 'NGMap',
  data() {
    return {
      x: 0,
      y: 0,
      r: 0
    }
  },
  mounted() {
    var vm = this;
    ipc.on('can-loc-reply',(event, x, y, r) => {
      vm.x = x;
      vm.y = y;
      vm.r = r;
      console.log("location-vm", x, y, r);
    });

    setInterval(() => { this.poll() }, 250);
  },
  methods: {
    poll: function() {
      ipc.send('can-loc-poll');
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#pointer {
  background-image: url('../assets/img/pointer.png');
  position: absolute;
  height: 32px;
  width: 25px;
  background-size: contain;
  left: 543px;
  top: 241px;
}
#ngmap {
    background-image: url('../assets/img/italyMap.jpg');
    position: absolute;
    z-index: -1;
    height: 4096px;
    width: 4096px;
    left: calc(-2048px + 562px);
    top: calc(-2048px + 264px);
    transform-origin: center;
}
</style>

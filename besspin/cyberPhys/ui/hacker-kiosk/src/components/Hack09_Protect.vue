<!--

"SSITH protects systems common means of exploitation"

ToDO: 
* @losborn  each button has to send a message so we can switch the scenarios!

-->
<template>
  <div id="hack09">
      <button class="hack09-info-btn img-btn" @click="protectInfo()">
      </button>
      <button class="hack09-crit-btn img-btn" @click="protectCrit()">
      </button>
  </div>
</template>

<style scoped>
  #hack09 {
    background-image: url('/hack09_protect/hack09_protect.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack09-info-btn {
    background-image: url('/hack09_protect/hack09_protect_hackInfo_btn.png');
    width: 450px;
    height: 180px;
    top: 1610px;
    left: 85px;
    background-position: -20px;
  }
  .hack09-info-btn:active {
    background-image: url('/hack09_protect/hack09_protect_hackInfo_btnHIT.png');
    background-position-x: -5px;
  }
  .hack09-crit-btn {
    background-image: url('/hack09_protect/hack09_protect_hackCrit_btn.png');
    width: 450px;
    height: 180px;
    top: 1610px;
    left: 535px;
    background-position-x: -20px;
  }
  .hack09-crit-btn:active {
    background-image: url('/hack09_protect/hack09_protect_hackCrit_btnHIT.png');
    background-position-x: -5px;
    background-position-y: 17px;
  }
</style>


<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  export default {
    name: 'Hack09_Protect',
    props: {
    },
    data() {
      return {
        messages: [],
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
    },
    methods: {
    protectCrit() {
      ipc.send('button-pressed', 'ssith_ecu', []);
      this.$router.push({ name: 'hack12_protect_critical' });
    },
    protectInfo() {
      ipc.send('button-pressed', 'ssith_infotainment', []);
      this.$router.push({ name: 'hack10_protect_info_attempt' });
    },
    }
  };
</script>

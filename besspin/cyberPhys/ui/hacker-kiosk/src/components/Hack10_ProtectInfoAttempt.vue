<!--

"SSITH Protection enabled (Secure Infotainment scenario)"

TODO:
* @losborn we need to show a hack failure here - perhaps mirror the logic for the baseline scenario?
-->
<template>
  <div id="hack10">
      <!-- Data Exfil Button -->
      <button class="hack10-exfil-btn img-btn" @click="exfil()"></button>

      <div id="exfil-msg" class="status-msg">{{ exfilMessage }}</div>

      <!-- Radio Station Buttons -->
      <button class="hack10-station1-btn img-btn" @click="changeStation(1)"></button>
      <button class="hack10-station2-btn img-btn" @click="changeStation(2)"></button>
      <button class="hack10-station3-btn img-btn" @click="changeStation(3)"></button>

      <div id="station-msg" class="status-msg">{{ stationMessage }}</div>

      <!-- Volume Buttons -->
      <button class="hack10-down-btn img-btn" @click="volumeDown()"></button>
      <button class="hack10-up-btn img-btn" @click="volumeUp()"></button>

      <div id="volume-msg" class="status-msg">{{ volumeMessage }}</div>

      <router-link v-if="clickCount >= 1" class="hack10-next-btn img-btn" to="/hack11_protect_info_stop" tag="button">
      </router-link>

  </div>
</template>

<style scoped>

  .status-msg {
    font-size: 2em;
    font-family: 'Roboto Mono', monospace;
    position: absolute;
    width: 810px;
    left: 120px;
  }
  #volume-msg {
    top: 1520px;
  }
  #station-msg {
    top: 1050px;
  }
  #exfil-msg {
    top: 580px;
  }

  #hack10 {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }

   .hack10-exfil-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_gps_btn.png');
    width: 555px;
    height: 170px;
    top: 375px;
    left: 260px;
  }
  .hack10-exfil-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_gps_btn_HIT.png');
    background-position-x: 20px;
  }

  .hack10-station1-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn1.png');
    background-position-x: -20px;
    width: 220px;
    height: 170px;
    top: 852px;
    left: 200px;
  }
  .hack10-station1-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn1_HIT.png');
  }

  .hack10-station2-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn2.png');
    background-position-x: -20px;
    width: 220px;
    height: 170px;
    top: 852px;
    left: 420px;
  }
  .hack10-station2-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn2_HIT.png');
  }

  .hack10-station3-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn3.png');
    background-position-x: -20px;
    width: 220px;
    height: 170px;
    top: 852px;
    left: 640px;
  }
  .hack10-station3-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn3_HIT.png');
    background-position-x: -45px;
    background-position-y: -25px;
  }

  .hack10-up-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_up_btn.png');
    width: 250px;
    height: 170px;
    top: 1320px;
    left: 290px;
  }
  .hack10-up-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_up_btnHIT.png');
  }

  .hack10-down-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_down_btn.png');
    width: 250px;
    height: 170px;
    top: 1320px;
    left: 540px;
  }
  .hack10-down-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_down_btnHIT.png');
  }


  .hack10-next-btn {
    background-image: url('/hack13_protectCriticalStop/hack13_protectCriticalStop_continue_btn.png');
    width: 500px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack10-next-btn:active {
    background-image: url('/hack13_protectCriticalStop/hack13_protectCriticalStop_continue_btnHIT.png');
    background-position-x: 15px;
    background-position-y: 15px;
  }


</style>


<script>

  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  export default {
    name: 'Hack10_ProtectInfoAttempt',
    props: {
    },
    data() {
      return {
        messages: [],
        clickCount: 0,
        stationMessage: "",
        exfilMessage: "",
        volumeMessage: "",
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
      ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          // TODO: how to show a hack failure? `status` != 200? Or in `retval`?
          if(item.func == this.$options.name + '_changeStation' && item.status == 200) {
            this.stationMessage = "Station set to " + item.retval;
          } else if (item.func == this.$options.name + '_volumeUp' && item.status == 200) {
            this.volumeMessage = "Volume Increased";
          } else if (item.func == this.$options.name + '_volumeDown' && item.status == 200) {
            this.volumeMessage = "Volume Decreased";
          } else if (item.func == this.$options.name + '_exfil') {
            this.exfilMessage = item.retval.toString();
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
      exfil() {
        console.log("[click] data Exfil");
        this.clickCount++;
        ipc.send('button-pressed', this.$options.name + '_exfil', {});
      },
      changeStation(which) {
        console.log("[click] change to station ", which)
        this.clickCount++;
        ipc.send('button-pressed', this.$options.name + '_changeStation', which);
      },
      volumeUp() {
        console.log("[click] volumeUp")
        this.clickCount++;
        ipc.send('button-pressed', this.$options.name + '_volumeUp',{});
      },
      volumeDown() {
        console.log("[click] volumeDown");
        this.clickCount++;
        ipc.send('button-pressed', this.$options.name + '_volumeDown',{});
      }
    }
  };
</script>

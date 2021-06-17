<!--

"SSITH Protection enabled (Secure ECU scenario)"

TODO:
* @podhrmic hack OTA server again, so CHERI FreeRTOS can be hacked (based on the previous scenario switch)
* @losborn add logic for the buttons - they change only if the hack is OK, mirror the logic from the baseline scenario
--> 
<template>
  <div id="hack12">
      <!-- TODO: mirror behavior from Hack8_page so the buttons can change colors -->
      <!--
      <router-link class="hack12-brake-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-accel-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-steering-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-trans-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>
      -->

      <button :class="[!brakeECUOn ? 'hack08-brakes-btn-active' : '', 'hack12-brake-btn', 'img-btn']" @click="toggleBrakes()">
      </button>

      <button :class="[!acceleratorNormal ? 'hack08-accel-btn-active' : '', 'hack12-accel-btn', 'img-btn']" @click="toggleAccel()">
      </button>

      <button :class="[!lkaOn ? 'hack08-steer-btn-active' : '', 'hack12-steering-btn', 'img-btn']" @click="toggleSteering()">
      </button>

      <button :class="[!transDrive ? 'hack08-trans-btn-active' : '', 'hack12-trans-btn', 'img-btn']" @click="toggleTrans()">
      </button>

      <!--button v-if="clickCount >= 1" @click="next()" class="hack08-next-btn img-btn"></button-->
      <router-link v-if="clickCount >= 1" class="hack08-next-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>


  </div>
</template>

<style scoped>
  #hack12 {
    /* TODO: Replace with BG image that has button subtitles */
    background-image: url('/hack12_protectCritical/hack12_protectCritical_protected_critInput_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }

  .hack12-brake-btn {
    top: 1320px;
    left: 200px;
    width: 330px;
    height: 160px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_brakes_btn.png');
    background-position-x: -15px;
    background-position-y: -15px;
  }
  .hack12-brake-btn:active {
    background-image: url('/hack12_protectCritical/hack12_protectCritical_brakes_btnHIT.png');
    background-position-x: 0px;
    background-position-y: 0px;
  }

  .hack12-accel-btn {
    top: 1320px;
    left: 560px;
    width: 330px;
    height: 160px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_accel_btn.png');
    background-position-x: -15px;
    background-position-y: -15px;
  }
  .hack12-accel-btn:active {
    background-image: url('/hack12_protectCritical/hack12_protectCritical_accel_btnHIT.png');
    background-position-x: 0px;
    background-position-y: 0px;
  }

  .hack12-steering-btn {
    top: 1550px;
    left: 200px;
    width: 330px;
    height: 160px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_steering_btn.png');
    background-position-x: -15px;
    background-position-y: -15px;
  }
  .hack12-steering-btn:active {
    background-image: url('/hack12_protectCritical/hack12_protectCritical_steering_btnHIT.png');
    background-position-x: 0px;
    background-position-y: 0px;
  }
  .hack12-trans-btn {
    top: 1550px;
    left: 560px;
    width: 330px;
    height: 160px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_tran_btn.png');
    background-position-x: -15px;
    background-position-y: -15px;
  }
  .hack12-trans-btn:active {
    background-image: url('/hack12_protectCritical/hack12_protectCritical_tran_btnHIT.png');
    background-position-x: 0px;
    background-position-y: 0px;
  }
</style>


<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  export default {
    name: 'Hack12_ProtectCritical',
    props: {
    },
    data() {
      return {
        brakeECUOn: true,
        acceleratorNormal: true,
        lkaOn: true,
        transDrive: true,
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
       ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          if (item.func == 'critical_exploit' && item.status == 200) {
            if(item.args == 'brakes') {
              this.brakeECUOn = item.retval;
            } else if (item.args == 'throttle') {
              this.acceleratorNormal = item.retval;
            } else if (item.args == 'lkas') {
              this.lkaOn = item.retval;
            } else if (item.args == 'transmission') {
              this.transDrive = item.retval;
            }
          }
        });
      });
    },
    methods: {
      pollState() {
        ipc.send('zmq-poll', []);
      },
      toggleBrakes() {
        this.clickCount++;
        console.log("[click] brakeECUOn = " + this.brakeECUOn);
        ipc.send('button-pressed', 'critical_exploit', 'brakes');
      },
      toggleAccel() {
        this.clickCount++;
        console.log("[click] acceleratorNormal = " + this.acceleratorNormal);
        ipc.send('button-pressed', 'critical_exploit', 'throttle');
      },
      toggleSteering() {
        this.clickCount++;
        console.log("[click] lkaOn = " + this.lkaOn);
        ipc.send('button-pressed', 'critical_exploit', 'lkas');
      },
      toggleTrans() {
        this.clickCount++;
        console.log("[click] transDrive = " + this.transDrive);
        ipc.send('button-pressed', 'critical_exploit', 'transmission');
      }
    }
  };
</script>

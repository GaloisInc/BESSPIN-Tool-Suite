<!--

"SSITH Protection enabled (Secure ECU scenario)"

TODO:
* @podhrmic hack OTA server again, so CHERI FreeRTOS can be hacked (based on the previous scenario switch)
--> 
<template>
  <div id="hack12">
      <video :class="webcamEnabled ? 'webcamFeed' : ''" autoplay="true" id="videoElement" loop>
        <source src="/videos/hack15_solution.webm" type="video/webm">
      </video>
      <div id="bg"></div>

      <button :class="[!brakeECUOn ? 'hack08-brakes-btn-active' : '', 'hack12-brake-btn', 'img-btn']" @click="toggleBrakes()">
      </button>

      <button :class="[!acceleratorNormal ? 'hack08-accel-btn-active' : '', 'hack12-accel-btn', 'img-btn']" @click="toggleAccel()">
      </button>

      <button :class="[!lkaOn ? 'hack08-steer-btn-active' : '', 'hack12-steering-btn', 'img-btn']" @click="toggleSteering()">
      </button>

      <button :class="[!transDrive ? 'hack08-trans-btn-active' : '', 'hack12-trans-btn', 'img-btn']" @click="toggleTrans()">
      </button>

      <!-- <router-link v-if="clickCount >= 1" class="hack08-next-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link> -->
      <button v-if="clickCount >= 1" @click="next()" class="hack12-next-btn img-btn"></button>



  </div>
</template>

<style scoped>
  #bg {
    /* TODO: Replace with BG image that has button subtitles */
    background-image: url('/hack12_protectCritical/hack12_protectCritical_protected_critInput_noBTN.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  .webcamFeed {
    position: absolute;
    margin: auto;
    top: 540px;
    left: 75px;
    height: 670px;
  }
  #hack12 {
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
  .hack12-next-btn {
    background-image: url('/hack14_existential/hack14_existential_continue_btn.png');
    width: calc(716px * .7);
    height: calc(272px * .7);
    background-size: 70%;
    top: 1700px;
    left: 340px;
  }
</style>


<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  const { Atem } = require('atem-connection')
  const myAtem = new Atem()
  myAtem.on('info', console.log)
  myAtem.on('error', console.error)

  myAtem.connect('192.168.10.240') // Use the default static IP

  myAtem.on('ATEM: StateChanged', (state, pathToChange) => {
    console.log(state) // catch the ATEM state.
  })

  const hacks = {
    NONE: 0,
    BRAKES: 1,
    STEER: 2,
    TRANS: 3,
    ACCEL: 4,
  }

  const transHackSrc = "/videos/hack12_protectCritical_protected_critInput TRANS.webm"
  const accelHackSrc = "/videos/hack12_protectCritical_protected_critInput ACCEL.webm"

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
        clickCount: 0,
        webcamEnabled: false,
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
      next() {
        ipc.send('button-pressed', 'next', []);
        this.$router.push({ name: 'hack13_protect_critical_stop' });
      },
      enableWebcamFeed(feed_id) {
        var video = document.querySelector("#videoElement");
        if (navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({ video: true })
          .then( (stream) => {
            video.srcObject = stream;
          })
          .catch( () => {
            console.log("Unable to initialize webcam feed ", feed_id);
          });
        }
      },

      // The video feed on this page has 5 different states.
      // 1. No hack selected
      // 2. Brakes (Webcam Feed)
      // 3. Steering (Webcam Feed)
      // 4. Transmission
      // 5. Accelerator
      swapVideoFeed(feed_id) {
        this.webcamEnabled = false;
        var video = document.querySelector("#videoElement");
        if(feed_id == hacks.STEER || feed_id == hacks.BRAKES) {
          this.webcamEnabled = true;
          this.enableWebcamFeed(feed_id);
          if (feed_id == hacks.STEER) {
            myAtem.changeProgramInput(1).then(() => {
            console.log("ATEM: Switched to Steering Cam (1)");
          });
          } else {
              myAtem.changeProgramInput(2).then(() => {
                console.log("ATEM: Switched to Brakes Cam (2)");
              });
          }
        } else if(feed_id == hacks.TRANS) {
          video.srcObject = null;
          video.src =  transHackSrc;
        } else if(feed_id == hacks.ACCEL) {
          video.srcObject = null;
          video.src = accelHackSrc;
        }
      },
      pollState() {
        ipc.send('zmq-poll', []);
      },
      toggleBrakes() {
        this.clickCount++;
        console.log("[click] brakeECUOn = " + this.brakeECUOn);
        ipc.send('button-pressed', 'critical_exploit', 'brakes');
        this.swapVideoFeed(hacks.BRAKES);
      },
      toggleAccel() {
        this.clickCount++;
        console.log("[click] acceleratorNormal = " + this.acceleratorNormal);
        ipc.send('button-pressed', 'critical_exploit', 'throttle');
        this.swapVideoFeed(hacks.ACCEL);
      },
      toggleSteering() {
        this.clickCount++;
        console.log("[click] lkaOn = " + this.lkaOn);
        ipc.send('button-pressed', 'critical_exploit', 'lkas');
        this.swapVideoFeed(hacks.STEER);
      },
      toggleTrans() {
        this.clickCount++;
        console.log("[click] transDrive = " + this.transDrive);
        ipc.send('button-pressed', 'critical_exploit', 'transmission');
        this.swapVideoFeed(hacks.TRANS);
      }
    }
  };
</script>

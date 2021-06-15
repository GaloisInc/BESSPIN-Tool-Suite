<!-- TODO: hack OTA server again, so CHERI FreeRTOS can be hacked -->
<!-- Show the output from CHERI to see how it mitigates the hacks? --> 
<template>
  <div id="hack12">
      <!-- TODO: mirror behavior from Hack8_page so the buttons can change colors -->
      <router-link class="hack12-brake-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-accel-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-steering-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
      </router-link>

      <router-link class="hack12-trans-btn img-btn" to="/hack13_protect_critical_stop" tag="button">
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
  export default {
    name: 'Hack12_ProtectCritical',
    props: {
    },
    data() {
      return {
        messages: []
      }
    },
    mounted() {
    },
    methods: {
    }
  };
</script>

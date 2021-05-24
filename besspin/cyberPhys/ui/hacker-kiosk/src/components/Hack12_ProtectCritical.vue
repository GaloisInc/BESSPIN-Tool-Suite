<template>
  <div id="hack12">

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
    top: 1220px;
    left: 200px;
    width: 716px;
    height: 272px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_brakes_btn.png');
  }
  .hack12-brake-btn:active {
    top: 1220px;
    left: 200px;
    width: 760px;
    height: 320px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_brakes_btnHIT.png');
  }

  .hack12-accel-btn {
    top: 1220px;
    left: 500px;
    width: 716px;
    height: 272px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_accel_btn.png');
  }
  .hack12-accel-btn:active {
    top: 1220px;
    left: 500px;
    width: 760px;
    height: 320px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_accel_btnHIT.png');
  }

  .hack12-steering-btn {
    top: 1520px;
    left: 200px;
    width: 716px;
    height: 272px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_steering_btn.png');
  }
  .hack12-steering-btn:active {
    top: 1520px;
    left: 200px;
    width: 760px;
    height: 320px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_steering_btnHIT.png');
  }
  .hack12-trans-btn {
    top: 1520px;
    left: 500px;
    width: 716px;
    height: 272px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_tran_btn.png');
  }
  .hack12-trans-btn:active {
    top: 1520px;
    left: 500px;
    width: 760px;
    height: 320px;
    background-image: url('/hack12_protectCritical/hack12_protectCritical_tran_btnHIT.png');
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

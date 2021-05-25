<template>
  <div id="hack10">
      <router-link class="hack10-btn img-btn" to="/hack11_protect_info_stop" tag="button">
      </router-link>

      <!-- Data Exfil Button -->
      <router-link class="hack10-exfil-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>

      <!-- Radio Station Buttons -->
      <router-link class="hack10-station1-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>
      <router-link class="hack10-station2-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>
      <router-link class="hack10-station3-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>

      <!-- Volume Buttons -->
      <router-link class="hack10-up-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>
      <router-link class="hack10-down-btn img-btn" to="/hack11_protect_info_stop" tag="button"></router-link>


  </div>
</template>

<style scoped>
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
    top: 350px;
    left: 235px;
    width: 600px;
    height: 220px;
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_gps_btnHIT.png');
  }

  .hack10-station1-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn1.png');
    width: 555px;
    height: 170px;
    top: 852px;
    left: 260px;
  }
  .hack10-station1-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn1_HIT.png');
  }

  .hack10-station2-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn2.png');
    width: 555px;
    height: 170px;
    top: 852px;
    left: 460px;
  }
  .hack10-station2-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn2_HIT.png');
  }

  .hack10-station3-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn3.png');
    width: 555px;
    height: 170px;
    top: 852px;
    left: 660px;
  }
  .hack10-station3-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_radio_btn3_HIT.png');
  }

  .hack10-up-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_up_btn.png');
    width: 555px;
    height: 170px;
    top: 1320px;
    left: 300px;
  }
  .hack10-up-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_up_btnHIT.png');
  }

  .hack10-down-btn {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_down_btn.png');
    width: 555px;
    height: 170px;
    top: 1320px;
    left: 600px;
  }
  .hack10-down-btn:active {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_down_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack10_ProtectInfoAttempt',
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

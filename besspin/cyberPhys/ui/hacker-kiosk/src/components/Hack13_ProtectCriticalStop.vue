<!--

"SSITH Protection enabled (Secure ECU scenario)"

--> 
<template>
  <div id="hack13">

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack13_protectCriticalStop.webm" type="video/webm">
      </video>
      <!-- <div id="bg"></div> -->

      <router-link class="hack13-btn img-btn" to="/hack14_existential" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
 #bg {
    background-image: url('/hack13_protectCriticalStop/hack13_protectCriticalStop_noBTN.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack13 {
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack13-btn {
    background-image: url('/hack13_protectCriticalStop/hack13_protectCriticalStop_continue_btn.png');
    width: 716px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack13-btn:active {
    top: 1620px;
    left: 300px;
    width: 760px;
    height: 320px;
    background-image: url('/hack11_protectInfoStop/hack01_protectInfoStop_continue_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack13_ProtectCriticalStop',
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

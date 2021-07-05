<!--

"ATTEMPTING EXPLOIT OF CRITICAL SYSTEMS"

No action needed

-->
<template>
  <div id="hack07">

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack07_criticalAttempt.webm" type="video/webm">
      </video>
      <div id="bg"></div>

      <router-link class="hack07-btn img-btn" to="/hack08_critical_exploit" tag="button">
      </router-link>
  </div>
</template>

<style scoped>

 #bg {
    background-image: url('/hack07_criticalAttempt/hack07_criticalAttempt.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack07 {
    background-image: url('/hack07_criticalAttempt/hack07_criticalAttempt.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack07-btn {
    background-image: url('/hack07_criticalAttempt/hack07_criticalAttempt_btn.png');
    width: 716px;
    height: 272px;
    top: 1550px;
    left: 290px;
  }
  .hack07-btn:active {
    left: 270px;
    top: 1520px;
    background-image: url('/hack07_criticalAttempt/hack07_criticalAttempt_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack07_CriticalAttempt',
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

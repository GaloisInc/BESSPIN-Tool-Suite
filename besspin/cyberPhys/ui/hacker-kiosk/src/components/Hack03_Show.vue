<!--

"This demo will show..."

No action needed here

-->
<template>

  <div id="hack03_show">

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack03_show.webm" type="video/webm">
      </video>
      <div id="bg"></div>


      <router-link class="hack03-btn img-btn" to="/hack04_access" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #bg {
    background-image: url('/hack03_show/hack03_show.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack03_show {
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack03-btn {
    background-image: url('/hack03_show/hack03_show_btn.png');
    width: 870px;
    height: 300px;
    top: 1560px;
    left: 140px;
  }
  .hack03-btn:active {
    background-image: url('/hack03_show/hack03_show_btnHit.png');
    left: 104px;
    top: 1528px;
  }
</style>


<script>
  export default {
    name: 'Hack03_Show',
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

<template>
  <div id="hack09">
      <router-link class="hack09-info-btn img-btn" to="/hack10_protect_info_attempt" tag="button">
      </router-link>
      <router-link class="hack09-crit-btn img-btn" to="/hack10_protect_info_attempt" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack09 {
    background-image: url('/hack09_protect/hack09_protect_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack09-info-btn {
    background-image: url('/hack09_protect/hack09_protect_hackInfo_btn.png');
    width: 716px;
    height: 272px;
    top: 1610px;
    left: 75px;
  }
  .hack09-info-btn:active {
    left: 50px;
    top: 1520px;
    background-image: url('/hack09_protect/hack08_protect_hackInfo_btnHIT.png');
  }
  .hack09-crit-btn {
    background-image: url('/hack09_protect/hack09_protect_hackCrit_btn.png');
    width: 716px;
    height: 272px;
    top: 1610px;
    left: 515px;
  }
  .hack09-crit-btn:active {
    left: 270px;
    top: 1520px;
    background-image: url('/hack09_protect/hack08_protect_hackCrit_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack09_Protect',
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

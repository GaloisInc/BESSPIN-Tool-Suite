<!--

"SSITH protects systems common means of exploitation"

ToDO: 
* @losborn  each button has to send a message so we can switch the scenarios!

-->
<template>
  <div id="hack09">
      <router-link class="hack09-info-btn img-btn" to="/hack10_protect_info_attempt" tag="button">
      </router-link>
      <router-link class="hack09-crit-btn img-btn" to="/hack12_protect_critical" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack09 {
    background-image: url('/hack09_protect/hack09_protect.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack09-info-btn {
    background-image: url('/hack09_protect/hack09_protect_hackInfo_btn.png');
    width: 450px;
    height: 180px;
    top: 1610px;
    left: 85px;
    background-position: -20px;
  }
  .hack09-info-btn:active {
    background-image: url('/hack09_protect/hack09_protect_hackInfo_btnHIT.png');
    background-position-x: -5px;
  }
  .hack09-crit-btn {
    background-image: url('/hack09_protect/hack09_protect_hackCrit_btn.png');
    width: 450px;
    height: 180px;
    top: 1610px;
    left: 535px;
    background-position-x: -20px;
  }
  .hack09-crit-btn:active {
    background-image: url('/hack09_protect/hack09_protect_hackCrit_btnHIT.png');
    background-position-x: -5px;
    background-position-y: 17px;
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

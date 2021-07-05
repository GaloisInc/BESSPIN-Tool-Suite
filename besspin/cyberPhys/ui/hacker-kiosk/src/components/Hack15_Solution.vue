<!--

"Everything is hackable (Either Secure scenario)"

No action needed
--> 
<template>
  <div id="hack15">

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack15_solution.webm" type="video/webm">
      </video>
      <!-- <div id="bg"></div> -->

      <router-link v-if="canContinue" class="hack15-btn img-btn" to="/hack02_intro" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
 #bg {
    background-image: url('/hack15_solution/hack15_solution_noBTN.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack15 {
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
.hack15-btn {
    background-image: url('/hack15_solution/hack15_solution_btn.png');
    width: 716px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack15-btn:active {
    top: 1620px;
    left: 300px;
    width: 760px;
    height: 320px;
    background-image: url('/hack15_solution/hack15_solution_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack15_Solution',
    props: {
    },
    data() {
      return {
        canContinue: false
      }
    },
    mounted() {
      this.canContinue = false;
      setTimeout(this.revealRestart, 5000);
    },
    methods: {
      revealRestart() {
        this.canContinue = true;
      }
    }
  };
</script>

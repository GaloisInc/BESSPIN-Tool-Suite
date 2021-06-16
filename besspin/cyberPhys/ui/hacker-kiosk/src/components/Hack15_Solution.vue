<!--

"Everything is hackable (Either Secure scenario)"

TODO:
* @losborn Restart sends a message / calls restart function?
--> 
<template>
  <div id="hack15">
      <router-link v-if="canContinue" class="hack15-btn img-btn" to="/hack02_intro" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack15 {
    background-image: url('/hack15_solution/hack15_solution_noBTN.png');
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

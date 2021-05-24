<template>
  <div id="hack05_info_attempt">
      <router-link class="hack05-btn img-btn" to="/hack06_info_exploit" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack05_info_attempt {
    background-image: url('/hack05_infoAttempt/hack05_infoAttempt_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack05-btn {
    background-image: url('/hack05_infoAttempt/hack05_infoAttempt_btn.png');
    width: 716px;
    height: 272px;
    top: 1550px;
    left: 290px;
  }
  .hack05-btn:active {
    left: 270px;
    top: 1520px;
    background-image: url('/hack05_infoAttempt/hack05_infoAttempt_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack05_InfoAttempt',
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

<template>
  <div id="hack10">
      <router-link class="hack10-btn img-btn" to="/hack11_protect_info_stop" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack10 {
    background-image: url('/hack10_protectInfoAttempt/hack10_protectInfoAttempt_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
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

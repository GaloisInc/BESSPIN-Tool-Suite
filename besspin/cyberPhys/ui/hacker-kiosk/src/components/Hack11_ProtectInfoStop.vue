<template>
  <div id="hack11">
      <router-link class="hack11-btn img-btn" to="/hack12_protect_critical" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack11 {
    background-image: url('/hack11_protectInfoStop/hack11_protectInfoStop_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack11-btn {
    background-image: url('/hack11_protectInfoStop/hack11_protectInfoStop_continue_btn.png');
    width: 716px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack11-btn:active {
    top: 1620px;
    left: 300px;
    width: 760px;
    height: 320px;
    background-image: url('/hack11_protectInfoStop/hack01_protectInfoStop_continue_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack11_ProtectInfoStop',
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

<!--

"SSITH Protection enabled (Secure Infotainment scenario)"

TODO:
* @lolsborn animation to be here?
* @lolsborn Button to next page links to Hack14 page 
-->
<template>
  <div id="hack11">
      <router-link class="hack11-btn img-btn" to="/hack14_existential" tag="button">
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
    width: 480px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack11-btn:active {
    background-image: url('/hack11_protectInfoStop/hack11_protectInfoStop_continue_btnHIT.png');
    background-position-x: 15px;
    background-position-y: 15px;
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

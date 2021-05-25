<template>
  <div id="hack14">
      <router-link class="hack14-btn img-btn" to="/hack15_solution" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack14 {
    background-image: url('/hack14_existential/hack14_existential_outro_noBTN.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack14-btn {
    background-image: url('/hack14_existential/hack14_existential_continue_btn.png');
    width: 716px;
    height: 272px;
    top: 1620px;
    left: 300px;
  }
  .hack14-btn:active {
    top: 1620px;
    left: 300px;
    width: 760px;
    height: 320px;
    background-image: url('/hack14_existential/hack14_existential_continue_btnHIT.png');
  }
</style>


<script>
  export default {
    name: 'Hack14_Existential',
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

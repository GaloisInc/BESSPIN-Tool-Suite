<template>
  <div id="hack03_show">
      <router-link class="hack03-btn img-btn" to="/hack04_access" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack03_show {
    background-image: url('/hack03_show/hack03_show.png');
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

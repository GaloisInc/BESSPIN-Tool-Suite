<!-- TODO: the Next button here has to initialize the hack!-->
<template>
  <div id="hack04_access">
      <router-link class="hack04-btn img-btn" to="/hack05_info_attempt" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack04_access {
    background-image: url('/hack04_access/hack04_access.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack04-btn {
    background-image: url('/hack04_access/hack04_access_btn.png');
    width: 940px;
    height: 320px;
    top: 1560px;
    left: 100px;
  }
  .hack04-btn:active {
    background-image: url('/hack04_access/hack04_access_btnHIT.png');
    top:  1530px;
    left: 60px;
  }
</style>


<script>
  export default {
    name: 'Hack04_Access',
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

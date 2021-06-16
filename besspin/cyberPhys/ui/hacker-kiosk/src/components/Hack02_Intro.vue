<!--

INTRO PAGE

"We live in a hyper connected world"


TODO:
@podhrmic:
* Switch to Baseline Scenario
* reset what needs to be reset

-->
<template>
  <div id="hack02_intro">

      <router-link class="hack02-btn-back img-btn" to="/" tag="button">
      </router-link>

      <router-link class="hack02-btn img-btn" to="/hack03_show" tag="button">
      </router-link>
  </div>
</template>

<style scoped>
  #hack02_intro {
    background-image: url('/hack02_intro/hack02_intro.png');
    height: 1920px;
    width: 1080px;
    text-align: center;
  }
  .hack02-btn-back {
    width: 100px;
    height: 100px;
    top: 0;
    left: 0;
  }
  .hack02-btn {
    background-image: url('/hack02_intro/hack02_intro_btn.png');
    width: 716px;
    height: 272px;
    top: 1540px;
    left: 180px;
  }
  .hack02-btn:active {
    left: 150px;
    top: 1508px;
    width: 760px;
    height: 320px;
    background-image: url('/hack02_intro/hack02_intro_btnHIT.png');
  }
</style>

<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  export default {
    name: 'Hack02_Intro',
    props: {
    },
    data() {
      return {
        messages: []
      }
    },
    mounted() {
      // Reset Scenerio when the intro loads
      ipc.send('button-pressed', 'reset', []);
    },
    methods: {
    }
  };
</script>

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

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/H_2_Connected_World_v6.webm" type="video/webm">
      </video>
      <div id="bg"></div>

      <router-link class="hack02-btn-back img-btn" to="/" tag="button">
      </router-link>

      <button class="hack02-btn img-btn" @click="next()">
      </button>
  </div>
</template>

<style scoped>
  #bg {
    background-image: url('/hack02_intro/hack02_intro.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #videoElement {
    position: absolute;
    margin: auto;
    top: 580px;
    left:0px;
    height: 870px;
  }
  #hack02_intro {
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
        messages: [],
        clicked: false,
        resetSent: false,
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
      // Reset Scenerio when the intro loads
      if (!this.resetSent) {
        ipc.send('button-pressed', 'reset', {});
        this.resetSent = true
      }
      ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          console.log("item", item);
          if(item.func == 'hack02_next' && item.status == 200 && !this.clicked) {
            this.$router.push({ name: 'hack03_show' });
            this.clicked = true
          }
        });
      });
    },
    unmounted() {
      clearInterval(this.poller);
    },
    methods: {
      pollState() {
        ipc.send('zmq-poll', []);
      },
      next() {
        ipc.send('button-pressed', 'hack02_next', {});
        console.log('button-pressed', 'hack02_next',{});
      }
    }
  };
</script>

<!--

"ATTEMPTING EXPLOIT"
-->
<template>
  <div id="hack05_info_attempt">

      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack05_infoAttempt.webm" type="video/webm">
      </video>
      <div id="bg"></div>


    <button v-if="canContinue" class="hack05-btn img-btn" @click="hackInfotainment()"></button>
  </div>
</template>

<style scoped>
 #bg {
    background-image: url('/hack05_infoAttempt/hack05_infoAttempt.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack05_info_attempt {
    background-image: url('/hack05_infoAttempt/hack05_infoAttempt.png');
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

  const electron = require('electron')
  const ipc = electron.ipcRenderer;
  
  export default {
    name: 'Hack05_InfoAttempt',
    props: {
    },
    data() {
      return {
        messages: [],
        canContinue: false,
        clicked: false,
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
      this.canContinue = false;
      setTimeout(() => {this.canContinue = true}, 3000);

      ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          console.log("item", item);
          if(item.func == 'next' && item.status == 200 && !this.clicked) {
            this.$router.push({ name: 'hack06_info_exploit' });
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
      hackInfotainment() {
        ipc.send('button-pressed', 'hack05-next', {});
        console.log('button-pressed', 'hack05-next',{});
      }
    }
  };
</script>

<template>
  <div id="hack05_info_attempt">
    <button class="hack05-btn img-btn" @click="hackInfotainment()"></button>
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

  const electron = require('electron')
  const ipc = electron.ipcRenderer;
  
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
      let poller = setInterval(() => { this.pollState() }, 3000);
      let vm = this;
      ipc.on('state-change',(event, state) => {
        console.log('state change in render thread', state);
        if(state == "hack-info-success") {
          console.log('info hack successful, moving on');
          console.log(vm);
          vm.$router.push({ name: 'hack06_info_exploit' });
          clearInterval(poller);
        }
      });

    },
    methods: {
      pollState() {
        ipc.send('state-poll', []);
      },
      hackInfotainment() {
        ipc.send('cmd-msg', 'hack-info');
        console.log("Send hack for infotainment");
      }
    }
  };
</script>

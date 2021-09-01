<!--

"ACCESS THE CAR'S SYSTEMS BY ..."

TODO: 
* @podhrmic the Next button here has to initialize the hack! So the next screen can print the results...

-->
<template>

  <div id="hack04_access">


      <video autoplay="true" id="videoElement" loop>
        <source src="/videos/hack04_access.webm" type="video/webm">
      </video>
      <div id="bg"></div>

      <button class="hack04-btn img-btn" @click="next()">
      </button>
  </div>
</template>

<style scoped>
  #bg {
    background-image: url('/hack04_access/hack04_access.png');
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
  }
  #hack04_access {
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
  const electron = require('electron')
  const ipc = electron.ipcRenderer;

  export default {
    name: 'Hack04_Access',
    props: {
    },
    data() {
      return {
        messages: [],
        clicked: false,
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
      ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          console.log("item", item);
          if(item.func == 'hack04_next' && item.status == 200 && !this.clicked) {
            this.$router.push({ name: 'hack05_info_attempt' });
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
        ipc.send('button-pressed', 'hack04_next', {});
        console.log('button-pressed', 'hack04_next',{});
      }
    }
  };
</script>

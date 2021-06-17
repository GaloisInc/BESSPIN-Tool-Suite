<!--

"ACCESS THE CAR'S SYSTEMS BY ..."

TODO: 
* @podhrmic the Next button here has to initialize the hack! So the next screen can print the results...

-->
<template>
  <div id="hack04_access">
      <button class="hack04-btn img-btn" @click="next()">
      </button>
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
          if(item.func == 'next' && item.status == 200 && !this.clicked) {
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
        ipc.send('button-pressed', 'next', {});
        console.log('button-pressed', 'next',{});
      }
    }
  };
</script>

<!--

"ATTEMPTING EXPLOIT"

TODO: 
* @losborn Needs to show results from the `previous` page/button click - how? What about a IPC call upon loading?
* @losborn "next" should be available only after the exploit completes

-->
<template>
  <div id="hack05_info_attempt">
    <button class="hack05-btn img-btn" @click="hackInfotainment()"></button>
  </div>
</template>

<style scoped>
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
        poller: setInterval(() => { this.pollState() }, 500)
      }
    },
    mounted() {
      let vm = this;
      ipc.on('zmq-results',(event, q) => {
        q.forEach(item => {
          console.log("item", item);
          //TODO: Handle Failure?
          if(item.func == this.$options.name && item.status == 200) {
            vm.$router.push({ name: 'hack06_info_exploit' });
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
        ipc.send('button-pressed', this.$options.name, {});
        console.log('button-pressed', this.$options.name,{});
      }
    }
  };
</script>

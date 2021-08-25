<template>
  <div id="debug">
    <div id="stream-headers">
      <div class="header" v-if="message">
        DEBUG
      </div>
    </div>
    <div id="debug-stream">
      <div class="msg_data">{{ message }}</div>
    </div>
  </div>
</template>

<style scoped>
 @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
  #debug-stream {
    font-family: 'Roboto Mono', monospace;
    width: 350px;
    height: 400px;
    overflow: scroll;
    overflow-x: hidden;
    font-size: .8em;
  }
  #debug li {
    list-style-type: none;
    padding-left: 0;
  }
  .msg_timestamp, .msg_timestamp_header {
    width: 110px;
  }
  .msg_timestamp, .msg_id, .msg_data, .header {
    display: inline-block;
  }
  .msg_id, .msg_id_header {
    width: 140px;
  }
  .header {
    font-weight: bold;
  }
</style>

<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;
  export default {
    name: 'Console',
    props: {
    },
    data: function() {
      return {
        message: ''
      }
    },
    mounted: function() {
      var vm = this;
      ipc.on('debug-reply',(event, arg) => {
        vm.update(arg);
      });

      setInterval(() => { this.poll() }, 3000);
    },
    methods: {
      update: function(msg) {
        this.message = msg.message;
      },
      poll: function() {
        ipc.send('debug-poll', []);
      }
    }
  };
</script>

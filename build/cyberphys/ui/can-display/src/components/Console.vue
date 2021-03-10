<template>
  <div id="console">
    <h2>CAN Bus Data Stream</h2>
    <div id="stream-headers">
      <div class="header msg_id_header">
        CAN ID
      </div>
      <div class="header msg_timestamp_header">
        Timestamp
      </div>
      <div class="header msg_data_header">
        Data
      </div>
    </div>
    <div id="console-stream">
      <li v-for="message in messages" v-bind:key="message.timestamp">
      <div class="msg_id">0x{{ message.id.toString(16).toUpperCase() }}</div>
      <div class="msg_timestamp"> {{ message.timestamp }} </div>
      <div class="msg_data">{{ message.data }}</div>
      </li>
    </div>
  </div>
</template>

<style scoped>
 @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
  #console {
    margin-top: 300px;
    position: absolute;
    left: 500px;
  }
  #console-stream {
    font-family: 'Roboto Mono', monospace;
    width: 600px;
    height: 590px;
    /* border: 1px solid green; */
    overflow: scroll;
    overflow-x: hidden;
  }
  #console li {
    list-style-type: none;
    padding-left: 0;
  }
  .msg_timestamp, .msg_timestamp_header {
    width: 180px;
  }
  .msg_timestamp, .msg_id, .msg_data, .header {
    display: inline-block;
  }
  .msg_id, .msg_id_header {
    width: 110px;
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
        messages: []
      }
    },
    mounted: function() {
      var vm = this;
      ipc.on('can-reply',(event, arg) => {
        vm.update(arg);
      });

      setInterval(() => { this.poll() }, 3000);
    },
    methods: {
      update: function(messages) {
        var container = document.getElementById("console-stream");
        for(let m of messages) {
          this.messages.push(m);
        }
        if(this.messages.length>100) {
          this.messages = this.messages.slice(this.messages.length-100, this.messages.length);
        }
        container.scrollTop = container.scrollHeight - container.clientHeight;
      },
      poll: function() {
        ipc.send('can-poll', []);
      }
    }
  };
</script>

<template>
  <div id="hello">
    Hello
  </div>
</template>

<script>
  const electron = require('electron')
  const ipc = electron.ipcRenderer;
  export default {
    name: 'Hello',
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

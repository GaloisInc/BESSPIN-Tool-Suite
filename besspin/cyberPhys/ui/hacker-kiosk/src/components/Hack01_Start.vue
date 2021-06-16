<!--

DEMO SETUP PAGE

TODO:
* @losborn: add timeouts for *each* screen, so the demo can "self-hack" by self-pressing the buttons
-->
<template>
  <div id="hack01_start" class="hack-screen">
      <h1>Demo Setup</h1>


      <div class="demo-options">
        <button @click="enableTimer()">
          <strong>Demo Timer On</strong>
          <p>
            This option limits the dmeo time to 5 minutes.  This is
            useful when there is a line of people waiting their turn.
          </p>
        </button>

        <button @click="disableTimer()">
          <strong>Demo Timer Off</strong>
          <p>
            This option has no time limit.
          </p>
        </button>
      </div>
  </div>
</template>

<style scoped>
  h1 {
    padding-top: 150px;
    color: #707070;
    text-transform: uppercase;
    text-align: center;
    font-weight: 900;
  }
  .demo-options {
    text-align: center;
  }
  #hack01_start {
    background-color: #D2D2D2;
    min-height: 100vh;
    width: 100%;
  }
  button {
    background-color: white;
    color: #4E4E4E;
    width: 200px;
    height: 200px;
    /* display: inline; */
    border-radius: 15px;
    vertical-align: top;
    margin-right: 30px;
    font-size: .7em;
  }
  button > strong {
    text-transform: uppercase;
  }
</style>

<script>
  var globalTimer = undefined;
  export default {
    name: 'Hack01_Start',
    props: {
    },
    data() {
      return {
      }
    },
    mounted() {
    },
    methods: {
      disableTimer() {
        clearInterval(globalTimer);
        this.next();
      },
      resetTimer() {
        globalTimer = setInterval(() => { console.log('reset'); window.location = '/#/hack02_intro';}, 5 * 60 * 1000);
      },
      enableTimer() {
        this.resetTimer();
        this.next();
      },
      next() {
        this.$router.push({ name: 'hack02_intro' });
      }
    }
  };
</script>

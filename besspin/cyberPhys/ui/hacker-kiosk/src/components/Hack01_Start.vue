<template>
  <div id="hack01_start" class="hack-screen">
      <h1>Demo Setup</h1>

      <div class="demo-options">
        <router-link tag="button" to="/hack02_intro">
          <strong>Demo Timer On</strong>
          <p>
            This option limits the dmeo time to 5 minutes.  This is
            useful when there is a line of people waiting their turn.
          </p>
        </router-link>

        <router-link tag="button" to="/hack02_intro">
          <strong>Demo Timer Off</strong>
          <p>
            This option has no time limit.
          </p>
        </router-link>
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
  export default {
    name: 'Hack01_Start',
    props: {
    },
    data() {
      return {
        messages: []
      }
    },
    mounted() {
    },
    methods: {
    }
  };
</script>

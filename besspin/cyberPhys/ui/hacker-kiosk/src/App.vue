<template>
  <div id="app">
  <router-view></router-view>
  </div>
</template>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
  #app, body {
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    font-family: 'Roboto Mono', monospace;
    color: #ddd;
    background-color: #000;
    font-size: 1.2em;
  }
  .img-btn {
    background-color: transparent;
    background-repeat: no-repeat;
    position: absolute;
    /* border: 1px solid red; */
    border: none;
    padding: 0;
    outline: none;
  }
  .hack-screen {
    margin: 0;
    padding: 10px;
  }
</style>

<script>
export default {
  name: 'App',
}
</script>

<template>
  <div id="app">
  <router-view></router-view>
  </div>
</template>

<style>
  #app, body {
    overflow: hidden;
    margin: 0;
    padding: 0;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1.2em;
  }
  .img-btn {
    background-color: transparent;
    background-repeat: no-repeat;
    position: absolute;
    border: none;
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

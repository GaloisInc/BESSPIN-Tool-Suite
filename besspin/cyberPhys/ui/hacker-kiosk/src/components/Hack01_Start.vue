<!--
-->
<template>
  <div id="hack01_start" class="hack-screen">
  </div>
</template>

<style scoped>
</style>

<script>
  export default {
    name: 'Hack01_Start',
    props: {
    },
    data() {
      return {
      }
    },
    mounted() {
      this.next();
    },
    methods: {
      next() {
        this.$router.push({ name: 'hack02_intro' });
      }
    }
  };
</script>

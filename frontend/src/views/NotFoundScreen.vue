<template>
  <div class="page not-found">
    <h1 class="page-title">Page not found</h1>
    <p class="page-subtitle">This page does not exist or is available to staff only.</p>
    <action-button label="Go to cars" @click="$go('/cars')"></action-button>
  </div>
</template>

<script>
import ActionButton from '../comps/ActionButton.vue';

export default {
  components: { ActionButton }
};
</script>

<style scoped>
.not-found {
  text-align: center;
  padding-top: 120px;
}
</style>

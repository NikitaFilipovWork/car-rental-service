<template>
  <input-item
    :value="value"
    :label="label"
    :type="shown ? 'text' : 'password'"
    :placeholder="placeholder"
    :autocomplete="autocomplete"
    :error="error"
    @input="$emit('input', $event)"
    @enter="$emit('enter')"
  >
    <template #suffix>
      <svg
        class="eye"
        width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"
        @mousedown.prevent
        @click="shown = !shown"
      >
        <use :href="shown ? '/assets/icons/eye.svg#eye' : '/assets/icons/eye_crossed.svg#eye'"></use>
      </svg>
    </template>
  </input-item>
</template>

<script>
import InputItem from './InputItem.vue';

export default {
  components: { InputItem },
  props: {
    value: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: 'Password'
    },
    placeholder: {
      type: String,
      default: 'Password'
    },
    autocomplete: {
      type: String,
      default: 'current-password'
    },
    error: {
      type: String,
      default: ''
    }
  },
  data: () => ({
    shown: false
  })
};
</script>

<style scoped>
.eye {
  flex-shrink: 0;
  cursor: pointer;
  color: var(--black);
}
</style>

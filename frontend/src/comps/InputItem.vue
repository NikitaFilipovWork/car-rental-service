<template>
  <label class="input-item">
    <div v-if="label" class="label">{{ label }}</div>
    <div :class="['input-field', error && 'invalid']">
      <input
        :value="value"
        :type="type"
        :placeholder="placeholder"
        :min="min"
        :max="max"
        :step="step"
        :autocomplete="autocomplete"
        @input="$emit('input', $event.target.value)"
        @keyup.enter="$emit('enter')"
      />
      <slot name="suffix"></slot>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </label>
</template>

<script>
export default {
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    min: {
      type: [String, Number],
      default: null
    },
    max: {
      type: [String, Number],
      default: null
    },
    step: {
      type: [String, Number],
      default: null
    },
    autocomplete: {
      type: String,
      default: 'off'
    },
    error: {
      type: String,
      default: ''
    }
  }
};
</script>

<style scoped>
.input-item {
  display: block;
  width: 100%;
}

.input-field {
  height: 48px;
  background-color: var(--surface);
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: var(--radius);
  padding: 0 14px;
  border: 1px solid transparent;
}

.input-field:focus-within {
  border-color: var(--black);
  background-color: var(--white);
}

.input-field.invalid {
  border-color: var(--black);
  border-width: 2px;
}

input {
  border: none;
  outline: none;
  width: 100%;
  height: 100%;
  background: transparent;
}

input::placeholder {
  color: var(--muted);
}

.error {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
}
</style>

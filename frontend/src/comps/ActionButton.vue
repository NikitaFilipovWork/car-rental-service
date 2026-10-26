<template>
  <button
    :type="submit ? 'submit' : 'button'"
    :class="['action-button', type, width]"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    {{ loading ? 'Please wait…' : label }}
  </button>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'filled',
      validator: (val) => ['filled', 'outlined', 'ghost'].includes(val)
    },
    width: {
      type: String,
      default: 'normal',
      validator: (val) => ['small', 'normal', 'wide', 'full'].includes(val)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    submit: {
      type: Boolean,
      default: false
    }
  }
};
</script>

<style scoped>
.action-button {
  cursor: pointer;
  height: 48px;
  padding: 0 24px;
  font-size: 16px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  border: 2px solid var(--black);
  background-color: var(--black);
  color: var(--white);
  user-select: none;
  white-space: nowrap;
  transition: background-color 0.15s, color 0.15s;
}

.action-button:hover {
  background-color: #333;
  border-color: #333;
}

.outlined {
  background-color: var(--white);
  color: var(--black);
}

.outlined:hover {
  background-color: var(--black);
  border-color: var(--black);
  color: var(--white);
}

.ghost {
  background: none;
  border-color: transparent;
  color: var(--black);
  text-decoration: underline;
  padding: 0 8px;
}

.ghost:hover {
  background: none;
  border-color: transparent;
  color: var(--muted);
}

.small {
  height: 38px;
  padding: 0 16px;
  font-size: 14px;
}

.wide {
  min-width: 260px;
}

.full {
  width: 100%;
}

.action-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}
</style>

<template>
  <div
    ref="root"
    :class="['custom-select', shown && 'active']"
  >
    <div v-if="label" class="label">{{ label }}</div>
    <div class="selected" @click="shown = !shown" @mousedown.prevent>
      <span :class="!selectedOption && 'placeholder'">
        {{ selectedOption ? selectedOption.name : placeholder }}
      </span>
      <svg :class="['arrow', shown && 'toggled']" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <use href="/assets/icons/arrow.svg#arrow"></use>
      </svg>
    </div>
    <div v-if="shown" class="options-container">
      <div
        v-if="clearable"
        :class="['option', value === null && 'selected-option']"
        @click="select(null)"
      >
        {{ placeholder }}
      </div>
      <div
        v-for="option in options"
        :key="option.id"
        :class="['option', option.id === value && 'selected-option']"
        @click="select(option.id)"
      >
        <span>{{ option.name }}</span>
        <svg v-if="option.id === value" width="12" height="9" viewBox="0 0 12 9" fill="none" xmlns="http://www.w3.org/2000/svg">
          <use href="/assets/icons/check.svg#check"></use>
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: [String, Number],
      default: null
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Any'
    },
    options: {
      type: Array,
      default: () => []
    },
    clearable: {
      type: Boolean,
      default: true
    }
  },
  data: () => ({
    shown: false
  }),
  computed: {
    selectedOption () {
      return this.options.find(option => option.id === this.value) || null;
    }
  },
  mounted () {
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeDestroy () {
    document.removeEventListener('click', this.handleOutsideClick);
  },
  methods: {
    select (id) {
      this.shown = false;
      this.$emit('input', id);
    },
    handleOutsideClick (event) {
      if (this.shown && !this.$refs.root.contains(event.target)) this.shown = false;
    }
  }
};
</script>

<style scoped>
.custom-select {
  width: 100%;
  z-index: 1;
}

.active {
  z-index: 3;
}

.selected {
  height: 48px;
  background-color: var(--surface);
  border-radius: var(--radius);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 14px;
  border: 1px solid transparent;
  cursor: pointer;
  user-select: none;
}

.active .selected {
  border-color: var(--black);
  background-color: var(--white);
}

.placeholder {
  color: var(--muted);
}

.arrow {
  flex-shrink: 0;
  transition: transform 0.15s;
}

.arrow.toggled {
  transform: rotate(180deg);
}

.options-container {
  width: 100%;
  max-height: 240px;
  overflow-y: auto;
  background-color: var(--white);
  border: 1px solid var(--black);
  border-radius: var(--radius);
  margin-top: 6px;
  position: absolute;
  padding: 4px;
}

.option {
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-radius: 6px;
  cursor: pointer;
}

.option:hover {
  background-color: var(--surface);
}

.selected-option {
  font-weight: 600;
}
</style>

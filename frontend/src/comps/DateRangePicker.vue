<template>
  <div class="date-range-picker">
    <div v-if="label" class="label">{{ label }}</div>
    <v-date-picker
      :value="range"
      is-range
      color="gray"
      locale="en"
      :min-date="minDate"
      :popover="{ placement: 'bottom-start' }"
      @input="handleInput"
    >
      <template #default="{ inputValue, togglePopover }">
        <div class="field" @click="togglePopover()">
          <span :class="!inputValue.start && 'placeholder'">
            {{ inputValue.start ? `${inputValue.start} — ${inputValue.end}` : placeholder }}
          </span>
          <svg
            v-if="value"
            class="icon clear"
            width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"
            @click.stop="$emit('input', null)"
          >
            <use href="/assets/icons/cross.svg#cross"></use>
          </svg>
          <svg v-else class="icon" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <use href="/assets/icons/calendar.svg#calendar"></use>
          </svg>
        </div>
      </template>
    </v-date-picker>
  </div>
</template>

<script>
import moment from 'moment';

import { DATE_FORMAT } from '../utils.js';

export default {
  props: {
    // { start: 'YYYY-MM-DD', end: 'YYYY-MM-DD' } or null
    value: {
      type: Object,
      default: null
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Select dates'
    },
    minDate: {
      type: Date,
      default: () => new Date()
    }
  },
  computed: {
    range () {
      if (!this.value) return null;
      return {
        start: moment(this.value.start, DATE_FORMAT).toDate(),
        end: moment(this.value.end, DATE_FORMAT).toDate()
      };
    }
  },
  methods: {
    handleInput (range) {
      if (!range) {
        this.$emit('input', null);
        return;
      }
      this.$emit('input', {
        start: moment(range.start).format(DATE_FORMAT),
        end: moment(range.end).format(DATE_FORMAT)
      });
    }
  }
};
</script>

<style scoped>
.date-range-picker {
  width: 100%;
}

.field {
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

.field:hover {
  border-color: var(--black);
}

.placeholder {
  color: var(--muted);
}

.icon {
  flex-shrink: 0;
}

.clear:hover {
  color: var(--muted);
}
</style>

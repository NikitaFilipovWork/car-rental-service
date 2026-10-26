<template>
  <span :class="['status-badge', status.toLowerCase()]">{{ text }}</span>
</template>

<script>
import { PAYMENT_STATUSES, RENTAL_STATUSES, optionName } from '../utils.js';

export default {
  props: {
    status: {
      type: String,
      required: true
    }
  },
  computed: {
    text () {
      return optionName([...RENTAL_STATUSES, ...PAYMENT_STATUSES], this.status);
    }
  }
};
</script>

<style scoped>
/* Black and white only: statuses differ by fill, outline and pattern */
.status-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1.5px solid var(--black);
  white-space: nowrap;
}

.booked,
.pending {
  background-color: var(--black);
  color: var(--white);
}

.completed,
.paid {
  background-color: var(--white);
  color: var(--black);
}

.overdue {
  background: repeating-linear-gradient(45deg, var(--black) 0 6px, #444 6px 12px);
  color: var(--white);
}

.canceled,
.expired {
  border-style: dashed;
  border-color: var(--muted);
  color: var(--muted);
}
</style>

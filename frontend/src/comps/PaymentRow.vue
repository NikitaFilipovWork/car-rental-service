<template>
  <div class="payment-row">
    <div class="main">
      <span class="type">{{ typeName }}</span>
      <span class="muted">#{{ payment.id }}<template v-if="showRental"> · rental #{{ payment.rental }}</template></span>
    </div>
    <span class="amount">{{ formatMoney(payment.money_to_pay) }}</span>
    <status-badge :status="payment.status"></status-badge>
    <a
      v-if="payment.status === 'PENDING' && payment.session_url"
      class="pay"
      :href="payment.session_url"
      target="_blank"
      rel="noopener"
    >Pay</a>
    <span v-else class="pay-placeholder"></span>
  </div>
</template>

<script>
import { PAYMENT_TYPES, formatMoney, optionName } from '../utils.js';
import StatusBadge from './StatusBadge.vue';

export default {
  components: { StatusBadge },
  props: {
    payment: {
      type: Object,
      required: true
    },
    showRental: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    typeName () {
      return optionName(PAYMENT_TYPES, this.payment.type);
    }
  },
  methods: {
    formatMoney
  }
};
</script>

<style scoped>
.payment-row {
  display: grid;
  grid-template-columns: 1fr auto auto 72px;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background-color: var(--white);
}

.main {
  display: flex;
  flex-direction: column;
}

.type {
  font-weight: 700;
}

.main .muted {
  font-size: 13px;
}

.amount {
  font-weight: 700;
  font-size: 17px;
}

.pay {
  text-align: center;
  font-weight: 700;
  text-decoration: none;
  padding: 8px 0;
  border-radius: var(--radius);
  background-color: var(--black);
  color: var(--white);
}

.pay:hover {
  background-color: #333;
}

@media (max-width: 560px) {
  .payment-row {
    grid-template-columns: 1fr auto;
  }
}
</style>

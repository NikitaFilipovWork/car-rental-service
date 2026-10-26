<template>
  <div class="page result">
    <div v-if="state === 'loading'" class="card">
      <h1 class="page-title">Checking your payment…</h1>
      <p class="page-subtitle">Please wait, we are confirming the payment with Stripe.</p>
    </div>

    <div v-else-if="state === 'paid'" class="card">
      <div class="icon filled">
        <svg width="28" height="21" viewBox="0 0 12 9" fill="none" xmlns="http://www.w3.org/2000/svg">
          <use href="/assets/icons/check.svg#check"></use>
        </svg>
      </div>
      <h1 class="page-title">Payment successful</h1>
      <p class="page-subtitle">Thank you! Your payment is confirmed.</p>

      <dl class="summary">
        <div><dt>Amount</dt><dd>{{ formatMoney(payment.money_to_pay) }}</dd></div>
        <div><dt>For</dt><dd>{{ typeName }}</dd></div>
        <div v-if="payment.rental"><dt>Car</dt><dd>{{ payment.rental.car }}</dd></div>
        <div v-if="payment.rental">
          <dt>Dates</dt>
          <dd>{{ formatDate(payment.rental.start_date) }} — {{ formatDate(payment.rental.end_date) }}</dd>
        </div>
      </dl>

      <div class="actions">
        <action-button label="My rentals" @click="$go('/rentals')"></action-button>
        <action-button label="All payments" type="outlined" @click="$go('/payments')"></action-button>
      </div>
    </div>

    <div v-else class="card">
      <div class="icon">
        <svg width="24" height="24" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <use href="/assets/icons/cross.svg#cross"></use>
        </svg>
      </div>
      <h1 class="page-title">Payment not confirmed</h1>
      <p class="page-subtitle">{{ message }}</p>
      <div class="actions">
        <action-button label="Go to payments" @click="$go('/payments')"></action-button>
      </div>
    </div>
  </div>
</template>

<script>
import { errorMessage } from '../api.js';
import { PAYMENT_TYPES, formatDate, formatMoney, optionName } from '../utils.js';
import ActionButton from '../comps/ActionButton.vue';

export default {
  components: { ActionButton },
  data: () => ({
    state: 'loading',
    payment: null,
    message: ''
  }),
  computed: {
    typeName () {
      return optionName(PAYMENT_TYPES, this.payment.type);
    }
  },
  created () {
    // Stripe puts session_id in the query: /?session_id=cs_...#/payments/success
    const sessionId = new URLSearchParams(location.search).get('session_id');
    if (!sessionId) {
      this.state = 'error';
      this.message = 'There is no payment to confirm. Open your payments to check their status.';
      return;
    }
    this.confirm(sessionId);
  },
  methods: {
    formatDate,
    formatMoney,

    async confirm (sessionId) {
      try {
        const { data } = await this.$api.get('/payments/success/', {
          params: { session_id: sessionId }
        });
        this.payment = data;
        this.state = 'paid';
        // Drop session_id from the address bar, it is not needed any more
        history.replaceState(null, '', `${location.pathname}${location.hash}`);
      } catch (error) {
        const status = error.response && error.response.status;
        const messages = {
          400: 'Stripe has not received the money yet. If you closed the payment page, pay again from your payments.',
          404: 'This payment was not found. Open your payments to check their status.'
        };
        this.state = 'error';
        this.message = messages[status] || errorMessage(error);
      }
    }
  }
};
</script>

<style scoped>
.result {
  display: flex;
  justify-content: center;
  padding-top: 80px;
}

.card {
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 32px;
  border: 2px solid var(--black);
  border-radius: var(--radius);
}

.icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid var(--black);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.icon.filled {
  background-color: var(--black);
  color: var(--white);
}

.summary {
  width: 100%;
  margin-bottom: 28px;
  border-top: 1px solid var(--border);
}

.summary > div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 700;
  text-align: right;
}

.actions {
  justify-content: center;
}
</style>

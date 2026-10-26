<template>
  <div class="page">
    <h1 class="page-title">Payments</h1>
    <p class="page-subtitle">
      {{ user.is_staff ? 'Payments of all customers.' : 'Unpaid payments have a Pay button that opens Stripe.' }}
    </p>

    <div class="toolbar">
      <custom-select v-model="status" class="filter" label="Status" :options="statuses"></custom-select>
      <custom-select v-model="type" class="filter" label="Type" :options="types"></custom-select>
    </div>

    <div v-if="$route.query.canceled" class="canceled-banner">
      Payment was not completed. You can pay later with the <strong>Pay</strong> button,
      the Stripe link works for 24 hours.
    </div>

    <div v-if="pendingTotal" class="pending-banner">
      You have unpaid payments for <strong>{{ formatMoney(pendingTotal) }}</strong> on this page.
    </div>

    <div v-if="loading && !payments.length" class="empty">Loading payments…</div>
    <div v-else-if="error" class="empty">{{ error }}</div>
    <div v-else-if="!payments.length" class="empty">No payments found.</div>
    <div v-else class="payments">
      <payment-row v-for="payment in payments" :key="payment.id" :payment="payment" show-rental></payment-row>
    </div>

    <pagination-controls :page="page" :count="count" @change="changePage"></pagination-controls>
  </div>
</template>

<script>
import { errorMessage } from '../api.js';
import { PAYMENT_STATUSES, PAYMENT_TYPES, formatMoney } from '../utils.js';
import CustomSelect from '../comps/CustomSelect.vue';
import PaginationControls from '../comps/PaginationControls.vue';
import PaymentRow from '../comps/PaymentRow.vue';

export default {
  components: { CustomSelect, PaginationControls, PaymentRow },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    payments: [],
    count: 0,
    page: 1,
    status: null,
    type: null,
    loading: false,
    error: '',
    statuses: PAYMENT_STATUSES,
    types: PAYMENT_TYPES
  }),
  computed: {
    pendingTotal () {
      if (this.user.is_staff) return 0;
      return this.payments
        .filter(payment => payment.status === 'PENDING')
        .reduce((sum, payment) => sum + Number(payment.money_to_pay), 0);
    }
  },
  watch: {
    status () {
      this.page = 1;
      this.fetchPayments();
    },
    type () {
      this.page = 1;
      this.fetchPayments();
    }
  },
  created () {
    this.fetchPayments();
  },
  methods: {
    formatMoney,

    async fetchPayments () {
      const params = { page: this.page };
      if (this.status) params.status = this.status;
      if (this.type) params.type = this.type;

      this.loading = true;
      this.error = '';
      try {
        const { data } = await this.$api.get('/payments/', { params });
        this.payments = data.results;
        this.count = data.count;
      } catch (error) {
        this.error = errorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    changePage (page) {
      this.page = page;
      this.fetchPayments();
      window.scrollTo(0, 0);
    }
  }
};
</script>

<style scoped>
.filter {
  width: 240px;
}

.pending-banner {
  padding: 16px 20px;
  margin-bottom: 20px;
  border-radius: var(--radius);
  background-color: var(--black);
  color: var(--white);
}

.canceled-banner {
  padding: 16px 20px;
  margin-bottom: 20px;
  border-radius: var(--radius);
  border: 2px solid var(--black);
}

.payments {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@media (max-width: 720px) {
  .filter {
    width: 100%;
  }
}
</style>

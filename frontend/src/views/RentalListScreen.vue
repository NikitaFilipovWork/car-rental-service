<template>
  <div class="page">
    <h1 class="page-title">{{ user.is_staff ? 'All rentals' : 'My rentals' }}</h1>
    <p class="page-subtitle">{{ count }} {{ count === 1 ? 'rental' : 'rentals' }}</p>

    <div class="toolbar">
      <custom-select v-model="status" class="filter" label="Status" :options="statuses"></custom-select>
      <input-item
        v-if="user.is_staff"
        v-model="userId"
        class="filter"
        label="User ID"
        type="number"
        placeholder="Any user"
      ></input-item>
    </div>

    <div v-if="loading && !rentals.length" class="empty">Loading rentals…</div>
    <div v-else-if="error" class="empty">{{ error }}</div>
    <div v-else-if="!rentals.length" class="empty">
      No rentals yet. <a class="link" href="#/cars">Find a car</a>
    </div>

    <div v-else class="rental-list">
      <div v-for="rental in rentals" :key="rental.id" class="rental">
        <div class="rental-head" @click="toggle(rental)">
          <div class="car">
            <span class="car-name">{{ rental.car }}</span>
            <span class="muted">
              #{{ rental.id }}<template v-if="user.is_staff"> · {{ rental.user }}</template>
            </span>
          </div>
          <div class="dates">
            <span>{{ formatDate(rental.start_date) }} — {{ formatDate(rental.end_date) }}</span>
            <span class="muted">
              {{ rentalDays(rental.start_date, rental.end_date) }} days · {{ formatMoney(rental.price_per_day) }} / day
            </span>
          </div>
          <status-badge :status="rental.status"></status-badge>
          <svg :class="['arrow', expandedId === rental.id && 'toggled']" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <use href="/assets/icons/arrow.svg#arrow"></use>
          </svg>
        </div>

        <div v-if="expandedId === rental.id" class="rental-body">
          <div class="facts">
            <div><span class="muted">Rental price</span> <strong>{{ formatMoney(rentalTotal(rental)) }}</strong></div>
            <div v-if="rental.actual_return_date">
              <span class="muted">Returned</span> <strong>{{ formatDate(rental.actual_return_date) }}</strong>
            </div>
          </div>

          <div class="actions">
            <action-button
              v-if="canReturn(rental)"
              label="Return car"
              width="small"
              :loading="actionId === rental.id"
              @click="returnRental(rental)"
            ></action-button>
            <action-button
              v-if="canCancel(rental)"
              label="Cancel booking"
              type="outlined"
              width="small"
              :loading="actionId === rental.id"
              @click="cancelRental(rental)"
            ></action-button>
          </div>

          <div>
            <div class="payments-title">Payments</div>
            <div v-if="!details[rental.id]" class="muted">Loading…</div>
            <div v-else-if="!details[rental.id].payments.length" class="muted">
              No payments yet. They are created when the car is returned or the booking is canceled late.
            </div>
            <div v-else class="payments">
              <payment-row v-for="payment in details[rental.id].payments" :key="payment.id" :payment="payment"></payment-row>
            </div>
          </div>
        </div>
      </div>
    </div>

    <pagination-controls :page="page" :count="count" @change="changePage"></pagination-controls>
  </div>
</template>

<script>
import debounce from 'lodash.debounce';
import moment from 'moment';

import { errorMessage } from '../api.js';
import { RENTAL_STATUSES, formatDate, formatMoney, rentalDays, today } from '../utils.js';
import ActionButton from '../comps/ActionButton.vue';
import CustomSelect from '../comps/CustomSelect.vue';
import InputItem from '../comps/InputItem.vue';
import PaginationControls from '../comps/PaginationControls.vue';
import PaymentRow from '../comps/PaymentRow.vue';
import StatusBadge from '../comps/StatusBadge.vue';

export default {
  components: { ActionButton, CustomSelect, InputItem, PaginationControls, PaymentRow, StatusBadge },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    rentals: [],
    count: 0,
    page: 1,
    status: null,
    userId: '',
    loading: false,
    error: '',
    expandedId: null,
    details: {},
    actionId: null,
    statuses: RENTAL_STATUSES
  }),
  watch: {
    status () {
      this.page = 1;
      this.fetchRentals();
    },
    userId () {
      this.page = 1;
      this.debouncedFetch();
    }
  },
  created () {
    this.debouncedFetch = debounce(this.fetchRentals, 400);
    this.fetchRentals();
  },
  methods: {
    formatDate,
    formatMoney,
    rentalDays,

    async fetchRentals () {
      const params = { page: this.page };
      if (this.status) params.status = this.status;
      if (this.userId) params.user_id = this.userId;

      this.loading = true;
      this.error = '';
      try {
        const { data } = await this.$api.get('/rentals/', { params });
        this.rentals = data.results;
        this.count = data.count;
      } catch (error) {
        this.error = errorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async fetchDetails (rentalId) {
      try {
        const { data } = await this.$api.get(`/rentals/${rentalId}/`);
        this.$set(this.details, rentalId, data);
      } catch (error) {
        this.$notify.error(errorMessage(error));
      }
    },

    toggle (rental) {
      this.expandedId = this.expandedId === rental.id ? null : rental.id;
      if (this.expandedId) this.fetchDetails(rental.id);
    },

    changePage (page) {
      this.page = page;
      this.expandedId = null;
      this.fetchRentals();
      window.scrollTo(0, 0);
    },

    rentalTotal (rental) {
      return rentalDays(rental.start_date, rental.end_date) * Number(rental.price_per_day);
    },

    canReturn (rental) {
      return ['BOOKED', 'OVERDUE'].includes(rental.status) && today() >= rental.start_date;
    },

    canCancel (rental) {
      return rental.status === 'BOOKED' && today() < rental.start_date;
    },

    async returnRental (rental) {
      const overdue = today() > rental.end_date;
      const message = overdue
        ? 'Return this car? It is overdue, so an overdue fee (150% of the daily price per extra day) will be added.'
        : 'Return this car now?';
      if (!window.confirm(message)) return;

      await this.runAction(rental, 'return', 'Car returned. Please pay for the rental below.');
    },

    async cancelRental (rental) {
      const dayBefore = moment(rental.start_date).diff(moment(today()), 'days') <= 1;
      const message = dayBefore
        ? 'Cancel this booking? It starts tomorrow, so a cancellation fee of 50% will be charged.'
        : 'Cancel this booking? It is free.';
      if (!window.confirm(message)) return;

      await this.runAction(rental, 'cancel', dayBefore
        ? 'Booking canceled. Please pay the cancellation fee below.'
        : 'Booking canceled.');
    },

    async runAction (rental, action, successMessage) {
      this.actionId = rental.id;
      try {
        const { data } = await this.$api.post(`/rentals/${rental.id}/${action}/`);
        Object.assign(rental, {
          status: data.status,
          actual_return_date: data.actual_return_date
        });
        this.$set(this.details, rental.id, data);
        this.$notify.success(successMessage);
      } catch (error) {
        this.$notify.error(errorMessage(error));
      } finally {
        this.actionId = null;
      }
    }
  }
};
</script>

<style scoped>
.filter {
  width: 240px;
}

.rental-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rental {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.rental-head {
  display: grid;
  grid-template-columns: 1.3fr 1.3fr auto 20px;
  align-items: center;
  gap: 20px;
  padding: 18px 20px;
  cursor: pointer;
}

.rental-head:hover {
  background-color: var(--surface);
}

.car,
.dates {
  display: flex;
  flex-direction: column;
}

.car-name {
  font-weight: 700;
  font-size: 16px;
}

.muted {
  font-size: 13px;
}

.arrow {
  transition: transform 0.15s;
}

.arrow.toggled {
  transform: rotate(180deg);
}

.rental-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  border-top: 1px solid var(--border);
  background-color: #fafafa;
}

.facts {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
}

.facts > div {
  display: flex;
  flex-direction: column;
}

.actions:empty {
  display: none;
}

.payments-title {
  font-weight: 700;
  margin-bottom: 10px;
}

.payments {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (max-width: 720px) {
  .filter {
    width: 100%;
  }

  .rental-head {
    grid-template-columns: 1fr auto;
  }

  .dates {
    grid-row: 2;
  }

  .arrow {
    display: none;
  }
}
</style>

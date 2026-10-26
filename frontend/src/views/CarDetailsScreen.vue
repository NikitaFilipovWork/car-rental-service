<template>
  <div class="page">
    <a class="back link" href="#/cars">← All cars</a>

    <div v-if="loading" class="empty">Loading…</div>
    <div v-else-if="error" class="empty">{{ error }}</div>

    <div v-else class="details">
      <car-image class="photo" :src="car.image" :alt="title"></car-image>

      <div class="side">
        <h1 class="page-title">{{ title }}</h1>
        <p class="page-subtitle">{{ car.year }} · {{ fuelName }}</p>

        <dl class="specs">
          <div><dt>Price</dt><dd>{{ formatMoney(car.daily_rate) }} / day</dd></div>
          <div><dt>Year</dt><dd>{{ car.year }}</dd></div>
          <div><dt>Fuel</dt><dd>{{ fuelName }}</dd></div>
          <div><dt>Cars in fleet</dt><dd>{{ car.inventory }}</dd></div>
        </dl>

        <form class="booking" @submit.prevent="book">
          <div class="section-title">Book this car</div>
          <date-range-picker v-model="dates" label="Rental dates" placeholder="Choose start and end date"></date-range-picker>

          <div v-if="dates" class="summary">
            <span>{{ formatMoney(car.daily_rate) }} × {{ days }} {{ days === 1 ? 'day' : 'days' }}</span>
            <strong>{{ formatMoney(total) }}</strong>
          </div>
          <p class="muted note">You pay when you return the car. Cancellation is free up to two days before the start, the day before it costs 50%.</p>

          <action-button
            label="Book now"
            width="full"
            submit
            :disabled="!dates || !car.inventory"
            :loading="booking"
          ></action-button>
          <p v-if="!car.inventory" class="muted note">This car is not available for rent.</p>
        </form>

        <div v-if="user.is_staff" class="staff-actions">
          <div class="section-title">Staff actions</div>
          <div class="actions">
            <action-button label="Edit car" type="outlined" @click="$go(`/cars/${car.id}/edit`)"></action-button>
            <action-button label="Delete" type="ghost" :loading="deleting" @click="deleteCar"></action-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { errorMessage } from '../api.js';
import { FUEL_TYPES, formatMoney, optionName, rentalDays } from '../utils.js';
import ActionButton from '../comps/ActionButton.vue';
import CarImage from '../comps/CarImage.vue';
import DateRangePicker from '../comps/DateRangePicker.vue';

export default {
  components: { ActionButton, CarImage, DateRangePicker },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    car: null,
    loading: true,
    error: '',
    dates: null,
    booking: false,
    deleting: false
  }),
  computed: {
    carId () {
      return this.$route.segments[1];
    },
    title () {
      return `${this.car.brand} ${this.car.model}`;
    },
    fuelName () {
      return optionName(FUEL_TYPES, this.car.fuel_type);
    },
    days () {
      return this.dates ? rentalDays(this.dates.start, this.dates.end) : 0;
    },
    total () {
      return this.days * Number(this.car.daily_rate);
    }
  },
  created () {
    this.fetchCar();
  },
  methods: {
    formatMoney,

    async fetchCar () {
      this.loading = true;
      try {
        const { data } = await this.$api.get(`/cars/${this.carId}/`);
        this.car = data;
      } catch (error) {
        this.error = error.response && error.response.status === 404
          ? 'This car does not exist.'
          : errorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    async book () {
      if (!this.dates) return;

      this.booking = true;
      try {
        await this.$api.post('/rentals/', {
          car: this.car.id,
          start_date: this.dates.start,
          end_date: this.dates.end
        });
        this.$notify.success(`${this.title} is booked. See it in your rentals.`);
        this.$go('/rentals');
      } catch (error) {
        this.$notify.error(errorMessage(error));
      } finally {
        this.booking = false;
      }
    },

    async deleteCar () {
      if (!window.confirm(`Delete ${this.title}? This cannot be undone.`)) return;

      this.deleting = true;
      try {
        await this.$api.delete(`/cars/${this.car.id}/`);
        this.$notify.success(`${this.title} was deleted.`);
        this.$go('/cars');
      } catch (error) {
        this.$notify.error(errorMessage(error));
      } finally {
        this.deleting = false;
      }
    }
  }
};
</script>

<style scoped>
.back {
  display: inline-block;
  margin-bottom: 24px;
  text-decoration: none;
}

.details {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 40px;
  align-items: start;
}

.photo {
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.side {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.side .page-subtitle {
  margin: -20px 0 0;
}

.specs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.specs > div {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}

.specs > div:nth-child(odd) {
  border-right: 1px solid var(--border);
}

.specs > div:nth-last-child(-n + 2) {
  border-bottom: none;
}

dt {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

dd {
  margin: 0;
  font-weight: 700;
  font-size: 17px;
}

.booking {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  border: 2px solid var(--black);
  border-radius: var(--radius);
}

.booking .section-title {
  margin-bottom: 0;
}

.summary {
  display: flex;
  justify-content: space-between;
  font-size: 17px;
}

.note {
  font-size: 13px;
}

@media (max-width: 860px) {
  .details {
    grid-template-columns: 1fr;
  }
}
</style>

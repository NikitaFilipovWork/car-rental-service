<template>
  <div class="page">
    <div class="title-row">
      <div>
        <h1 class="page-title">Cars</h1>
        <p class="page-subtitle">{{ subtitle }}</p>
      </div>
      <action-button v-if="user.is_staff" label="Add car" @click="$go('/cars/new')"></action-button>
    </div>

    <div class="filters">
      <input-item v-model="filters.search" class="search" label="Search" placeholder="Brand or model"></input-item>
      <date-range-picker v-model="filters.dates" label="Free on dates" placeholder="Any dates"></date-range-picker>
      <custom-select v-model="filters.fuel_type" label="Fuel" :options="fuelTypes"></custom-select>
      <custom-select v-model="filters.available" label="Availability" :options="availabilityOptions"></custom-select>
      <input-item v-model="filters.min_year" label="Year from" type="number" placeholder="e.g. 2018"></input-item>
      <input-item v-model="filters.max_year" label="Year to" type="number" placeholder="e.g. 2024"></input-item>
      <custom-select v-model="filters.ordering" label="Sort by" placeholder="Default" :options="orderingOptions"></custom-select>
      <action-button
        v-if="hasFilters"
        class="reset"
        label="Reset filters"
        type="ghost"
        @click="resetFilters"
      ></action-button>
    </div>

    <div v-if="loading && !cars.length" class="empty">Loading cars…</div>
    <div v-else-if="error" class="empty">{{ error }}</div>
    <div v-else-if="!cars.length" class="empty">No cars match these filters.</div>
    <div v-else :class="['car-grid', loading && 'loading']">
      <car-card v-for="car in cars" :key="car.id" :car="car"></car-card>
    </div>

    <pagination-controls :page="page" :count="count" @change="changePage"></pagination-controls>
  </div>
</template>

<script>
import debounce from 'lodash.debounce';

import { errorMessage } from '../api.js';
import { FUEL_TYPES } from '../utils.js';
import ActionButton from '../comps/ActionButton.vue';
import CarCard from '../comps/CarCard.vue';
import CustomSelect from '../comps/CustomSelect.vue';
import DateRangePicker from '../comps/DateRangePicker.vue';
import InputItem from '../comps/InputItem.vue';
import PaginationControls from '../comps/PaginationControls.vue';

const emptyFilters = () => ({
  search: '',
  dates: null,
  fuel_type: null,
  min_year: '',
  max_year: '',
  available: null,
  ordering: null
});

export default {
  components: { ActionButton, CarCard, CustomSelect, DateRangePicker, InputItem, PaginationControls },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    cars: [],
    count: 0,
    page: 1,
    loading: false,
    error: '',
    filters: emptyFilters(),
    fuelTypes: FUEL_TYPES,
    availabilityOptions: [
      { id: 'true', name: 'Available now' },
      { id: 'false', name: 'Not available' }
    ],
    orderingOptions: [
      { id: 'daily_rate', name: 'Price: low to high' },
      { id: '-daily_rate', name: 'Price: high to low' },
      { id: '-year', name: 'Newest first' },
      { id: 'year', name: 'Oldest first' },
      { id: 'brand', name: 'Brand A–Z' }
    ]
  }),
  computed: {
    subtitle () {
      if (this.filters.dates) return `${this.count} cars free for the selected dates`;
      return `${this.count} cars in our fleet`;
    },
    hasFilters () {
      return JSON.stringify(this.filters) !== JSON.stringify(emptyFilters());
    },
    params () {
      const { search, dates, ...rest } = this.filters;
      const params = { page: this.page };

      if (search.trim()) params.search = search.trim();
      if (dates) {
        params.start_date = dates.start;
        params.end_date = dates.end;
      }
      Object.entries(rest).forEach(([key, value]) => {
        if (value !== null && value !== '') params[key] = value;
      });
      return params;
    }
  },
  watch: {
    filters: {
      deep: true,
      handler () {
        this.page = 1;
        this.debouncedFetch();
      }
    }
  },
  created () {
    this.debouncedFetch = debounce(this.fetchCars, 400);
    this.fetchCars();
  },
  methods: {
    async fetchCars () {
      this.loading = true;
      this.error = '';
      try {
        const { data } = await this.$api.get('/cars/', { params: this.params });
        this.cars = data.results;
        this.count = data.count;
      } catch (error) {
        this.cars = [];
        this.count = 0;
        this.error = errorMessage(error);
      } finally {
        this.loading = false;
      }
    },

    changePage (page) {
      this.page = page;
      this.fetchCars();
      window.scrollTo(0, 0);
    },

    resetFilters () {
      this.filters = emptyFilters();
    }
  }
};
</script>

<style scoped>
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  align-items: end;
  margin-bottom: 36px;
  padding: 20px;
  /* keep dropdowns and the calendar above the car cards */
  z-index: 5;
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.reset {
  justify-self: start;
}

.car-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  transition: opacity 0.15s;
}

.car-grid.loading {
  opacity: 0.5;
}

@media (max-width: 1000px) {
  .filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .car-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .filters {
    grid-template-columns: 1fr;
  }

  .car-grid {
    grid-template-columns: 1fr;
  }

  .title-row {
    flex-direction: column;
  }
}
</style>

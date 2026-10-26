<template>
  <a class="car-card" :href="`#/cars/${car.id}`">
    <car-image :src="car.image" :alt="title" />
    <div class="info">
      <div class="title-row">
        <span class="title">{{ title }}</span>
        <span class="price">{{ formatMoney(car.daily_rate) }}<span class="muted"> / day</span></span>
      </div>
      <div class="tags">
        <span class="tag">{{ car.year }}</span>
        <span class="tag">{{ fuelName }}</span>
        <span :class="['tag', !car.inventory && 'tag-dark']">
          {{ car.inventory ? `${car.inventory} in fleet` : 'Not for rent' }}
        </span>
      </div>
    </div>
  </a>
</template>

<script>
import CarImage from './CarImage.vue';
import { FUEL_TYPES, formatMoney, optionName } from '../utils.js';

export default {
  components: { CarImage },
  props: {
    car: {
      type: Object,
      required: true
    }
  },
  computed: {
    title () {
      return `${this.car.brand} ${this.car.model}`;
    },
    fuelName () {
      return optionName(FUEL_TYPES, this.car.fuel_type);
    }
  },
  methods: {
    formatMoney
  }
};
</script>

<style scoped>
.car-card {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  text-decoration: none;
  background-color: var(--white);
  transition: border-color 0.15s, transform 0.15s;
}

.car-card:hover {
  border-color: var(--black);
  transform: translateY(-2px);
}

.info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: 700;
}

.price {
  font-weight: 700;
  white-space: nowrap;
}

.price .muted {
  font-weight: 500;
  font-size: 13px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background-color: var(--surface);
}

.tag-dark {
  background-color: var(--black);
  color: var(--white);
}
</style>

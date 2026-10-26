<template>
  <div class="page narrow">
    <a class="back link" :href="isEdit ? `#/cars/${carId}` : '#/cars'">← Back</a>
    <h1 class="page-title">{{ isEdit ? 'Edit car' : 'Add a car' }}</h1>
    <p class="page-subtitle">Fields marked with * are required.</p>

    <div v-if="loading" class="empty">Loading…</div>

    <form v-else class="form-grid" novalidate @submit.prevent="save">
      <image-uploader
        class="full"
        label="Photo"
        :current-image="currentImage"
        @upload="imageFile = $event"
      ></image-uploader>

      <input-item v-model="form.brand" label="Brand *" placeholder="Toyota" :error="errors.brand"></input-item>
      <input-item v-model="form.model" label="Model *" placeholder="Corolla" :error="errors.model"></input-item>
      <input-item
        v-model="form.year"
        label="Year *"
        type="number"
        min="1889"
        :max="currentYear"
        :placeholder="String(currentYear)"
        :error="errors.year"
      ></input-item>
      <div>
        <custom-select
          v-model="form.fuel_type"
          label="Fuel *"
          :options="fuelTypes"
          :clearable="false"
        ></custom-select>
        <div v-if="errors.fuel_type" class="error">{{ errors.fuel_type }}</div>
      </div>
      <input-item
        v-model="form.daily_rate"
        label="Price per day, $ *"
        type="number"
        min="0"
        step="0.01"
        placeholder="45.00"
        :error="errors.daily_rate"
      ></input-item>
      <input-item
        v-model="form.inventory"
        label="Number of cars *"
        type="number"
        min="0"
        placeholder="1"
        :error="errors.inventory"
      ></input-item>

      <div class="full actions">
        <action-button :label="isEdit ? 'Save changes' : 'Add car'" submit :loading="saving"></action-button>
        <action-button label="Cancel" type="outlined" @click="cancel"></action-button>
      </div>
    </form>
  </div>
</template>

<script>
import { errorMessage } from '../api.js';
import { FUEL_TYPES } from '../utils.js';
import ActionButton from '../comps/ActionButton.vue';
import CustomSelect from '../comps/CustomSelect.vue';
import ImageUploader from '../comps/ImageUploader.vue';
import InputItem from '../comps/InputItem.vue';

const FIELDS = ['brand', 'model', 'year', 'fuel_type', 'daily_rate', 'inventory'];

export default {
  components: { ActionButton, CustomSelect, ImageUploader, InputItem },
  data: () => ({
    form: {
      brand: '',
      model: '',
      year: '',
      fuel_type: 'GAS',
      daily_rate: '',
      inventory: '1'
    },
    currentImage: '',
    imageFile: null,
    errors: {},
    loading: false,
    saving: false,
    fuelTypes: FUEL_TYPES,
    currentYear: new Date().getFullYear()
  }),
  computed: {
    carId () {
      return this.$route.segments[1];
    },
    isEdit () {
      return this.carId !== 'new';
    }
  },
  watch: {
    form: {
      deep: true,
      handler () {
        if (Object.keys(this.errors).length) this.errors = {};
      }
    }
  },
  created () {
    if (this.isEdit) this.fetchCar();
  },
  methods: {
    async fetchCar () {
      this.loading = true;
      try {
        const { data } = await this.$api.get(`/cars/${this.carId}/`);
        FIELDS.forEach(field => { this.form[field] = String(data[field]); });
        this.currentImage = data.image || '';
      } catch (error) {
        this.$notify.error(errorMessage(error));
        this.$go('/cars');
      } finally {
        this.loading = false;
      }
    },

    validate () {
      const errors = {};
      FIELDS.forEach(field => {
        if (this.form[field] === '' || this.form[field] === null) errors[field] = 'This field is required.';
      });
      this.errors = errors;
      return !Object.keys(errors).length;
    },

    async save () {
      if (!this.validate()) return;

      this.saving = true;
      try {
        const request = this.isEdit
          ? this.$api.put(`/cars/${this.carId}/`, this.form)
          : this.$api.post('/cars/', this.form);
        const { data: car } = await request;

        if (this.imageFile) await this.uploadImage(car.id);

        this.$notify.success(this.isEdit ? 'Changes saved.' : `${car.brand} ${car.model} was added.`);
        this.$go(`/cars/${car.id}`);
      } catch (error) {
        const data = (error.response && error.response.data) || {};
        const fieldErrors = {};
        FIELDS.forEach(field => {
          if (data[field]) fieldErrors[field] = data[field].join(' ');
        });
        this.errors = fieldErrors;
        if (!Object.keys(fieldErrors).length) this.$notify.error(errorMessage(error));
      } finally {
        this.saving = false;
      }
    },

    async uploadImage (carId) {
      const formData = new FormData();
      formData.append('image', this.imageFile);

      try {
        await this.$api.post(`/cars/${carId}/upload-image/`, formData);
      } catch (error) {
        // The car itself is saved; only the photo failed
        this.$notify.error(`Car saved, but the photo was not uploaded: ${errorMessage(error)}`);
      }
    },

    cancel () {
      this.$go(this.isEdit ? `/cars/${this.carId}` : '/cars');
    }
  }
};
</script>

<style scoped>
.narrow {
  max-width: 760px;
}

.back {
  display: inline-block;
  margin-bottom: 24px;
  text-decoration: none;
}

.error {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
}

.actions {
  margin-top: 12px;
}
</style>

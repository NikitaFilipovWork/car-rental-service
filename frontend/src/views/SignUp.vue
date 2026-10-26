<template>
  <auth-layout title="Create an account" @submit="signUp">
    <template #subtitle>
      Already have an account? <a class="link" href="#/sign-in">Sign in</a>
    </template>
    <input-item
      v-model="email"
      label="Email"
      type="email"
      placeholder="you@example.com"
      autocomplete="email"
      :error="errors.email"
    ></input-item>
    <password-input
      v-model="password"
      placeholder="At least 5 characters"
      autocomplete="new-password"
      :error="errors.password"
    ></password-input>
    <password-input
      v-model="passwordRepeat"
      label="Repeat password"
      placeholder="Repeat password"
      autocomplete="new-password"
      :error="errors.passwordRepeat"
    ></password-input>
    <div v-if="errors.common" class="form-error">{{ errors.common }}</div>
    <action-button label="Sign up" width="full" submit :loading="loading"></action-button>
  </auth-layout>
</template>

<script>
import { errorMessage, tokens } from '../api.js';
import ActionButton from '../comps/ActionButton.vue';
import InputItem from '../comps/InputItem.vue';
import PasswordInput from '../comps/PasswordInput.vue';
import AuthLayout from './AuthLayout.vue';

export default {
  components: { ActionButton, AuthLayout, InputItem, PasswordInput },
  data: () => ({
    email: '',
    password: '',
    passwordRepeat: '',
    errors: {},
    loading: false
  }),
  methods: {
    validate () {
      const errors = {};
      if (!this.email) errors.email = 'Email is required.';
      if (this.password.length < 5) errors.password = 'Password must be at least 5 characters.';
      if (this.password !== this.passwordRepeat) errors.passwordRepeat = 'Passwords do not match.';
      this.errors = errors;
      return !Object.keys(errors).length;
    },

    async signUp () {
      if (!this.validate()) return;

      this.loading = true;
      try {
        await this.$api.post('/users/', { email: this.email, password: this.password });
        const { data } = await this.$api.post('/users/token/', {
          email: this.email,
          password: this.password
        });
        tokens.save(data);
        this.$notify.success('Welcome! Your account has been created.');
        this.$emit('log-in');
      } catch (error) {
        const data = (error.response && error.response.data) || {};
        this.errors = {
          email: data.email && data.email.join(' '),
          password: data.password && data.password.join(' '),
          common: !data.email && !data.password ? errorMessage(error) : ''
        };
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.form-error {
  font-weight: 600;
  padding: 12px 14px;
  border: 2px solid var(--black);
  border-radius: var(--radius);
}
</style>

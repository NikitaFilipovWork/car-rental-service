<template>
  <auth-layout title="Sign in" @submit="signIn">
    <template #subtitle>
      Not registered yet? <a class="link" href="#/sign-up">Create an account</a>
    </template>
    <input-item v-model="email" label="Email" type="email" placeholder="you@example.com" autocomplete="email"></input-item>
    <password-input v-model="password"></password-input>
    <div v-if="error" class="form-error">{{ error }}</div>
    <action-button label="Sign in" width="full" submit :loading="loading"></action-button>
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
    error: '',
    loading: false
  }),
  methods: {
    async signIn () {
      if (!this.email || !this.password) {
        this.error = 'Enter your email and password.';
        return;
      }

      this.loading = true;
      this.error = '';
      try {
        const { data } = await this.$api.post('/users/token/', {
          email: this.email,
          password: this.password
        });
        tokens.save(data);
        this.$emit('log-in');
      } catch (error) {
        this.error = error.response && error.response.status === 401
          ? 'Wrong email or password.'
          : errorMessage(error);
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

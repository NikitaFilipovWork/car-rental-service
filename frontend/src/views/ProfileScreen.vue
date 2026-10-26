<template>
  <div class="page narrow">
    <h1 class="page-title">Profile</h1>
    <p class="page-subtitle">
      Account #{{ user.id }}<template v-if="user.is_staff"> · Staff</template>
    </p>

    <form class="card" @submit.prevent="saveEmail">
      <div class="section-title">Email</div>
      <input-item v-model="email" label="Email" type="email" autocomplete="email" :error="emailError"></input-item>
      <action-button label="Save email" submit :disabled="email === user.email" :loading="savingEmail"></action-button>
    </form>

    <form class="card" @submit.prevent="savePassword">
      <div class="section-title">Change password</div>
      <password-input
        v-model="password"
        label="New password"
        placeholder="At least 5 characters"
        autocomplete="new-password"
        :error="passwordError"
      ></password-input>
      <password-input
        v-model="passwordRepeat"
        label="Repeat new password"
        placeholder="Repeat new password"
        autocomplete="new-password"
      ></password-input>
      <action-button label="Change password" submit :disabled="!password" :loading="savingPassword"></action-button>
    </form>
  </div>
</template>

<script>
import { errorMessage } from '../api.js';
import ActionButton from '../comps/ActionButton.vue';
import InputItem from '../comps/InputItem.vue';
import PasswordInput from '../comps/PasswordInput.vue';

export default {
  components: { ActionButton, InputItem, PasswordInput },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      email: this.user.email,
      emailError: '',
      password: '',
      passwordRepeat: '',
      passwordError: '',
      savingEmail: false,
      savingPassword: false
    };
  },
  methods: {
    async saveEmail () {
      this.savingEmail = true;
      this.emailError = '';
      try {
        const { data } = await this.$api.patch('/users/me/', { email: this.email });
        this.$emit('user-updated', data);
        this.$notify.success('Email updated.');
      } catch (error) {
        const data = (error.response && error.response.data) || {};
        this.emailError = data.email ? data.email.join(' ') : errorMessage(error);
      } finally {
        this.savingEmail = false;
      }
    },

    async savePassword () {
      if (this.password.length < 5) {
        this.passwordError = 'Password must be at least 5 characters.';
        return;
      }
      if (this.password !== this.passwordRepeat) {
        this.passwordError = 'Passwords do not match.';
        return;
      }

      this.savingPassword = true;
      this.passwordError = '';
      try {
        await this.$api.patch('/users/me/', { password: this.password });
        this.password = '';
        this.passwordRepeat = '';
        this.$notify.success('Password changed.');
      } catch (error) {
        const data = (error.response && error.response.data) || {};
        this.passwordError = data.password ? data.password.join(' ') : errorMessage(error);
      } finally {
        this.savingPassword = false;
      }
    }
  }
};
</script>

<style scoped>
.narrow {
  max-width: 560px;
}

.card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 24px;
}

.card .section-title {
  margin-bottom: 0;
}
</style>

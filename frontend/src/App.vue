<template>
  <div id="app">
    <div v-if="serverDown" class="page server-down">
      <h1 class="page-title">Server is not available</h1>
      <p class="page-subtitle">The API does not respond. It may still be starting, try again in a moment.</p>
      <button class="retry" @click="retry">Try again</button>
    </div>
    <template v-else-if="!checkingSession">
      <app-header v-if="user" :user="user" @log-out="logOut"></app-header>
      <main class="main">
        <component
          :is="screen"
          :key="$route.path"
          :user="user"
          @log-in="fetchUser"
          @user-updated="user = $event"
        ></component>
      </main>
      <app-footer></app-footer>
    </template>
    <app-notices></app-notices>
  </div>
</template>

<script>
import { tokens } from './api.js';

import AppHeader from './views/AppHeader.vue';
import AppFooter from './views/AppFooter.vue';
import AppNotices from './comps/AppNotices.vue';
import SignIn from './views/SignIn.vue';
import SignUp from './views/SignUp.vue';
import CarListScreen from './views/CarListScreen.vue';
import CarDetailsScreen from './views/CarDetailsScreen.vue';
import CarFormScreen from './views/CarFormScreen.vue';
import RentalListScreen from './views/RentalListScreen.vue';
import PaymentListScreen from './views/PaymentListScreen.vue';
import PaymentResultScreen from './views/PaymentResultScreen.vue';
import ProfileScreen from './views/ProfileScreen.vue';
import NotFoundScreen from './views/NotFoundScreen.vue';

export default {
  components: { AppHeader, AppFooter, AppNotices },
  data: () => ({
    user: null,
    checkingSession: true,
    serverDown: false
  }),
  computed: {
    screen () {
      const [section, id, action] = this.$route.segments;

      if (!this.user) return section === 'sign-up' ? SignUp : SignIn;

      if (section === 'cars') {
        if (id === 'new' || action === 'edit') return this.user.is_staff ? CarFormScreen : NotFoundScreen;
        if (id) return CarDetailsScreen;
        return CarListScreen;
      }

      if (section === 'payments' && id === 'success') return PaymentResultScreen;

      const screens = {
        rentals: RentalListScreen,
        payments: PaymentListScreen,
        profile: ProfileScreen
      };
      return screens[section] || NotFoundScreen;
    }
  },
  async created () {
    window.addEventListener('auth:logout', this.handleSessionExpired);

    if (tokens.access || tokens.refresh) await this.fetchUser();
    this.checkingSession = false;
  },
  beforeDestroy () {
    window.removeEventListener('auth:logout', this.handleSessionExpired);
  },
  methods: {
    async fetchUser () {
      try {
        const { data } = await this.$api.get('/users/me/');
        this.user = data;

        const { segments } = this.$route;
        if (!segments.length || ['sign-in', 'sign-up'].includes(segments[0])) this.$go('/cars');
      } catch (error) {
        const status = error.response && error.response.status;
        // Keep the tokens when the server is down; drop them only if they are invalid
        if (!status || status >= 500) {
          this.serverDown = true;
          return;
        }
        tokens.clear();
        this.user = null;
      }
    },

    async retry () {
      this.serverDown = false;
      this.checkingSession = true;
      await this.fetchUser();
      this.checkingSession = false;
    },

    logOut () {
      tokens.clear();
      this.user = null;
      this.$go('/sign-in');
    },

    handleSessionExpired () {
      if (!this.user) return;
      this.user = null;
      this.$notify.error('Your session has expired. Please sign in again.');
    }
  }
};
</script>

<style scoped>
.server-down {
  text-align: center;
  padding-top: 120px;
}

.retry {
  height: 48px;
  padding: 0 24px;
  border-radius: var(--radius);
  border: none;
  background-color: var(--black);
  color: var(--white);
  font-weight: 600;
  cursor: pointer;
}

.main {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
</style>

<template>
  <header class="header">
    <div class="header-inner">
      <a class="app-title" href="#/cars">Car Rental</a>
      <nav class="menu">
        <a href="#/cars" :class="section === 'cars' && 'active'">Cars</a>
        <a href="#/rentals" :class="section === 'rentals' && 'active'">
          {{ user.is_staff ? 'All rentals' : 'My rentals' }}
        </a>
        <a href="#/payments" :class="section === 'payments' && 'active'">Payments</a>
      </nav>
      <div ref="profile" class="profile-section">
        <button class="username" @click="showPopup = !showPopup">
          <span v-if="user.is_staff" class="staff">Staff</span>
          {{ user.email }}
          <svg width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <use href="/assets/icons/arrow.svg#arrow"></use>
          </svg>
        </button>
        <div v-if="showPopup" class="popup">
          <a href="#/profile" @click="showPopup = false">Profile</a>
          <a href="#/rentals" @click="showPopup = false">{{ user.is_staff ? 'All rentals' : 'My rentals' }}</a>
          <button @click="$emit('log-out')">Log out</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    showPopup: false
  }),
  computed: {
    section () {
      return this.$route.segments[0] || 'cars';
    }
  },
  mounted () {
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeDestroy () {
    document.removeEventListener('click', this.handleOutsideClick);
  },
  methods: {
    handleOutsideClick (event) {
      if (this.showPopup && !this.$refs.profile.contains(event.target)) this.showPopup = false;
    }
  }
};
</script>

<style scoped>
.header {
  background-color: var(--black);
  color: var(--white);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 72px;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 32px;
}

a {
  color: var(--white);
  text-decoration: none;
}

.app-title {
  font-weight: 900;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.menu {
  display: flex;
  gap: 4px;
  flex-grow: 1;
}

.menu a {
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: 500;
}

.menu a:hover {
  background-color: #262626;
}

.menu a.active {
  background-color: var(--white);
  color: var(--black);
  font-weight: 700;
}

.username {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--white);
  cursor: pointer;
  font-weight: 500;
}

.staff {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border: 1px solid var(--white);
  border-radius: 999px;
}

.popup {
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  min-width: 200px;
  background-color: var(--white);
  border: 1px solid var(--black);
  border-radius: var(--radius);
  padding: 6px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.popup a,
.popup button {
  color: var(--black);
  padding: 10px 12px;
  border-radius: 6px;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
}

.popup a:hover,
.popup button:hover {
  background-color: var(--surface);
}

@media (max-width: 720px) {
  .header-inner {
    padding: 12px 16px;
  }

  .menu {
    order: 3;
    width: 100%;
    overflow-x: auto;
  }

  .profile-section {
    margin-left: auto;
  }

  .username {
    max-width: 200px;
    overflow: hidden;
  }
}
</style>

<template>
  <div class="auth">
    <div class="auth-side">
      <span class="brand">Car Rental</span>
      <div>
        <div class="side-title">Book a car in a minute.</div>
        <div class="side-text">Pick the dates, choose a car and pay online.</div>
      </div>
    </div>
    <div class="auth-form-wrapper">
      <form class="auth-form" @submit.prevent="$emit('submit')">
        <h1 class="page-title">{{ title }}</h1>
        <p class="page-subtitle"><slot name="subtitle"></slot></p>
        <slot></slot>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    }
  }
};
</script>

<style scoped>
.auth {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: calc(100vh - 62px);
}

.auth-side {
  background-color: var(--black);
  color: var(--white);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand {
  font-weight: 900;
  font-size: 22px;
}

.side-title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 16px;
}

.side-text {
  color: #bdbdbd;
  font-size: 18px;
}

.auth-form-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
}

.auth-form {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.auth-form .page-subtitle {
  margin-bottom: 8px;
}

@media (max-width: 860px) {
  .auth {
    grid-template-columns: 1fr;
  }

  .auth-side {
    padding: 32px 24px;
    gap: 32px;
  }

  .side-title {
    font-size: 30px;
  }
}
</style>

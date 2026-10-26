<template>
  <div class="notices" aria-live="polite">
    <div
      v-for="notice in notices.items"
      :key="notice.id"
      :class="['notice', notice.type]"
    >
      <span>{{ notice.message }}</span>
      <svg
        class="close"
        width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"
        @click="dismiss(notice.id)"
      >
        <use href="/assets/icons/cross.svg#cross"></use>
      </svg>
    </div>
  </div>
</template>

<script>
import { dismiss, notices } from '../notify.js';

export default {
  data: () => ({
    notices
  }),
  methods: {
    dismiss
  }
};
</script>

<style scoped>
.notices {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: min(420px, calc(100vw - 48px));
}

.notice {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius);
  border: 2px solid var(--black);
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.success {
  background-color: var(--white);
  color: var(--black);
}

.error {
  background-color: var(--black);
  color: var(--white);
}

.close {
  flex-shrink: 0;
  cursor: pointer;
  margin-top: 2px;
}
</style>

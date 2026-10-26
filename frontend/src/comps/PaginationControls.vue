<template>
  <div v-if="totalPages > 1" class="pagination">
    <button class="move-btn" :disabled="page <= 1" aria-label="Previous page" @click="$emit('change', page - 1)">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <use href="/assets/icons/left_arrow.svg#left"></use>
      </svg>
    </button>
    <span class="info">Page {{ page }} of {{ totalPages }}</span>
    <button class="move-btn" :disabled="page >= totalPages" aria-label="Next page" @click="$emit('change', page + 1)">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <use href="/assets/icons/right_arrow.svg#right"></use>
      </svg>
    </button>
  </div>
</template>

<script>
// Backend PAGE_SIZE in core/settings.py
const PAGE_SIZE = 20;

export default {
  props: {
    page: {
      type: Number,
      default: 1
    },
    count: {
      type: Number,
      default: 0
    }
  },
  computed: {
    totalPages () {
      return Math.max(1, Math.ceil(this.count / PAGE_SIZE));
    }
  }
};
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 40px;
}

.move-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1.5px solid var(--black);
  background: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.move-btn:hover:not(:disabled) {
  background: var(--black);
  color: var(--white);
}

.move-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.info {
  font-weight: 600;
}
</style>

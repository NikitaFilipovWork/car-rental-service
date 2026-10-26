<template>
  <div class="car-image">
    <img v-if="src" :src="src" :alt="alt" />
    <div v-else class="no-photo">
      <svg width="64" height="40" viewBox="0 0 64 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 26l4-12a4 4 0 0 1 3.8-2.8h36.4A4 4 0 0 1 54 14l4 12v8h-5a5 5 0 0 1-10 0H21a5 5 0 0 1-10 0H6z" stroke="currentcolor" stroke-width="2.5" stroke-linejoin="round" />
      </svg>
      <span>No photo yet</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    src: {
      type: String,
      default: ''
    },
    alt: {
      type: String,
      default: ''
    }
  }
};
</script>

<style scoped>
.car-image {
  width: 100%;
  aspect-ratio: 16 / 10;
  background-color: var(--surface);
  overflow: hidden;
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.no-photo {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #b5b5b5;
  font-size: 13px;
  font-weight: 600;
}
</style>

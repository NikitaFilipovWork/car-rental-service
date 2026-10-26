<template>
  <footer class="footer">
    <div class="footer-inner">
      <span class="brand">Car Rental</span>
      <span class="muted">© {{ year }} Car Rental Service. All rights reserved.</span>
    </div>
  </footer>
</template>

<script>
export default {
  data: () => ({
    year: new Date().getFullYear()
  })
};
</script>

<style scoped>
.footer {
  border-top: 1px solid var(--border);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  font-size: 13px;
}

.brand {
  font-weight: 900;
}
</style>

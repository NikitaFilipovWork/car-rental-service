<template>
  <div class="image-uploader">
    <div class="label">{{ label }}</div>
    <label class="drop-zone">
      <img v-if="preview" :src="preview" alt="Car photo preview" class="preview" />
      <div v-else class="placeholder">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <use href="/assets/icons/plus.svg#plus"></use>
        </svg>
        <span>Choose a photo (JPG or PNG)</span>
      </div>
      <input
        ref="inputEl"
        class="file-input"
        type="file"
        accept=".png, .jpg, .jpeg, .webp"
        @change="handleFile"
      />
    </label>
    <div v-if="preview" class="hint muted">Click the photo to choose another one</div>
  </div>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      default: 'Photo'
    },
    // URL of the current image, shown until a new file is chosen
    currentImage: {
      type: String,
      default: ''
    }
  },
  data: () => ({
    localPreview: ''
  }),
  computed: {
    preview () {
      return this.localPreview || this.currentImage;
    }
  },
  beforeDestroy () {
    if (this.localPreview) URL.revokeObjectURL(this.localPreview);
  },
  methods: {
    handleFile () {
      const [file] = this.$refs.inputEl.files;
      if (!file) return;

      if (this.localPreview) URL.revokeObjectURL(this.localPreview);
      this.localPreview = URL.createObjectURL(file);
      this.$emit('upload', file);
    }
  }
};
</script>

<style scoped>
.drop-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: var(--surface);
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
}

.drop-zone:hover {
  border-color: var(--black);
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-weight: 600;
}

.preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
}

.hint {
  margin-top: 6px;
  font-size: 13px;
}
</style>

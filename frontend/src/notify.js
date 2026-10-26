import Vue from 'vue';

// Global toast messages shown by <app-notices>
export const notices = Vue.observable({ items: [] });

let nextId = 1;

function push (type, message, timeout = 5000) {
  const id = nextId++;
  notices.items.push({ id, type, message });
  setTimeout(() => dismiss(id), timeout);
}

export function dismiss (id) {
  notices.items = notices.items.filter(item => item.id !== id);
}

export default {
  success: (message) => push('success', message),
  error: (message) => push('error', message, 8000)
};

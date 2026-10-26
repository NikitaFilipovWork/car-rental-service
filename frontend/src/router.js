import Vue from 'vue';

// Minimal hash router: "#/cars/5?edit=true" -> { path: '/cars/5', segments: ['cars', '5'], query: { edit: 'true' } }
function parseHash () {
  const hash = location.hash.replace(/^#/, '') || '/cars';
  const [path, queryString = ''] = hash.split('?');
  const segments = path.split('/').filter(Boolean);
  const query = Object.fromEntries(new URLSearchParams(queryString));

  return { path, segments, query };
}

const route = Vue.observable(parseHash());

window.addEventListener('hashchange', () => {
  Object.assign(route, parseHash());
  window.scrollTo(0, 0);
});

function go (path) {
  location.hash = `#${path}`;
}

export default { route, go };

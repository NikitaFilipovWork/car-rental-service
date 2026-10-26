import axios from 'axios';

const ACCESS = 'access';
const REFRESH = 'refresh';

export const tokens = {
  get access () {
    return localStorage.getItem(ACCESS);
  },
  get refresh () {
    return localStorage.getItem(REFRESH);
  },
  save ({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear () {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  }
};

// Same origin: Vite proxies /api and /media to Django
const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  if (tokens.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

let refreshRequest = null;

function refreshAccessToken () {
  // Several requests may fail with 401 at once; refresh the token only once
  refreshRequest = refreshRequest || axios
    .post('/api/users/token/refresh/', { refresh: tokens.refresh })
    .then(({ data }) => tokens.save(data))
    .finally(() => { refreshRequest = null; });

  return refreshRequest;
}

api.interceptors.response.use(
  response => response,
  async (error) => {
    const { config, response } = error;
    const isAuthRequest = config && config.url.startsWith('/users/token');

    if (response && response.status === 401 && !config.retried && !isAuthRequest && tokens.refresh) {
      config.retried = true;
      try {
        await refreshAccessToken();
        return api(config);
      } catch (refreshError) {
        tokens.clear();
        window.dispatchEvent(new Event('auth:logout'));
      }
    }

    return Promise.reject(error);
  }
);

// Turns DRF error responses into one readable line
export function errorMessage (error) {
  const data = error && error.response && error.response.data;

  if (!error.response) return 'Server is not available. Try again later.';
  if (!data || typeof data !== 'object') return `Request failed (${error.response.status}).`;

  const collect = (value, field) => {
    if (Array.isArray(value)) return value.map(item => collect(item, field)).join(' ');
    if (value && typeof value === 'object') {
      return Object.entries(value).map(([key, item]) => collect(item, key)).join(' ');
    }
    const prefix = field && !['detail', 'non_field_errors'].includes(field) ? `${field}: ` : '';
    return `${prefix}${value}`;
  };

  return collect(data);
}

export default api;

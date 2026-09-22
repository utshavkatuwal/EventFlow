export const API_BASE = 'http://localhost:8000/api/v1';

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  };

  const token = localStorage.getItem('access_token');
  if (token && !config.headers.Authorization) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, config);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.message || 'Request failed');
  }

  return data;
}

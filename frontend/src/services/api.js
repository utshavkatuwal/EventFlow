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

  let res;
  try {
    res = await fetch(url, config);
  } catch {
    const err = new Error('Unable to connect to server. Is the backend running on http://localhost:8000?');
    err.status = 0;
    throw err;
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (!res.ok) {
    const message = typeof data?.detail === 'string' ? data.detail : (data?.detail?.message || data?.message || 'Request failed');
    const err = new Error(message);
    err.detail = data?.detail;
    err.status = res.status;
    throw err;
  }

  return data;
}

export async function apiUpload(path, formData, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { ...(options.headers || {}) };
  const token = localStorage.getItem('access_token');
  if (token && !headers.Authorization) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(url, { method: 'POST', body: formData, headers, ...options });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = {};
  }
  if (!res.ok) {
    const message = typeof data?.detail === 'string' ? data.detail : (data?.detail?.message || data?.message || 'Upload failed');
    const err = new Error(message);
    err.detail = data?.detail;
    err.status = res.status;
    throw err;
  }
  return data;
}

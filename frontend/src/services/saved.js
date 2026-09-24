import { apiFetch } from './api';

let cache = null;

export async function getSavedIds() {
  if (cache) return cache;
  try {
    const d = await apiFetch('/user/saved');
    cache = new Set((d?.items || []).map((e) => e.id));
  } catch {
    cache = new Set();
  }
  return cache;
}

export async function setSaved(eventId, save) {
  const res = await apiFetch(
    save ? '/favorites' : `/favorites/${eventId}`,
    save ? { method: 'POST', body: JSON.stringify({ event_id: eventId }) } : { method: 'DELETE' }
  );
  if (cache) {
    if (save) cache.add(eventId);
    else cache.delete(eventId);
  }
  return res;
}

export function clearSavedCache() {
  cache = null;
}

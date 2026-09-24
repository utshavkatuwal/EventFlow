// Vitest global setup for EventFlow frontend (jsdom).
// Kept dependency-free: no @testing-library required.
import { afterEach } from 'vitest';

afterEach(() => {
  document.body.innerHTML = '';
});

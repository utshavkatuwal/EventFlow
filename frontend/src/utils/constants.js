// EventFlow Frontend Constants

export const API_BASE = 'http://localhost:8000/api/v1';

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};

export const EVENT_STATUSES = ['DRAFT', 'PENDING_REVIEW', 'APPROVED', 'PUBLISHED', 'CANCELLED', 'COMPLETED', 'REJECTED'];

export const TICKET_STATUSES = ['VALID', 'USED', 'CANCELLED', 'EXPIRED'];

export const USER_ROLES = ['USER', 'ORGANIZER', 'ADMIN'];

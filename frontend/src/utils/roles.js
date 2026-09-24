/** Canonical role helpers — DB role is authoritative, never inferred. */

export function getRole(user) {
  if (!user) return null;
  const roles = Array.isArray(user.roles) ? user.roles.map((r) => String(r).toLowerCase()) : [];
  if (roles.includes('admin')) return 'admin';
  if (roles.includes('organizer')) return 'organizer';
  const accountType = String(user.account_type || user.role || 'user').toLowerCase();
  if (accountType === 'admin') return 'admin';
  if (accountType === 'organizer') return 'organizer';
  return 'user';
}

export function homeFor(role) {
  if (role === 'admin') return '/admin/dashboard';
  if (role === 'organizer') return '/organizer/dashboard';
  return '/user/dashboard';
}

export function homeForUser(user) {
  return homeFor(getRole(user));
}

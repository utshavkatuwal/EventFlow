import React from 'react';
import { apiFetch } from '../services/api';
import { homeForUser } from '../utils/roles';
import { clearSavedCache } from '../services/saved';

const AuthContext = React.createContext(null);

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('user')) || null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = React.useState(readStoredUser);
  const [authReady, setAuthReady] = React.useState(false);

  const persist = React.useCallback((userData, accessToken, refreshToken) => {
    setUser(userData);
    if (userData) localStorage.setItem('user', JSON.stringify(userData));
    else localStorage.removeItem('user');
    if (accessToken) localStorage.setItem('access_token', accessToken);
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
  }, []);

  const login = React.useCallback(
    (userData, accessToken, refreshToken) => persist(userData, accessToken, refreshToken),
    [persist]
  );

  const logout = React.useCallback(() => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    clearSavedCache();
  }, []);

  const refreshProfile = React.useCallback(async () => {
    try {
      const res = await apiFetch('/auth/me');
      const fresh = res?.data || res?.user;
      if (fresh) {
        persist(fresh, localStorage.getItem('access_token'), localStorage.getItem('refresh_token'));
        return fresh;
      }
    } catch (err) {
      // Expired/revoked token: drop stale session so guards reroute to login.
      if (err?.status === 401) logout();
      return null;
    }
    return null;
  }, [persist, logout]);

  // On boot AND refresh: revalidate with the backend (DB role is authoritative).
  React.useEffect(() => {
    let cancelled = false;
    async function boot() {
      if (localStorage.getItem('access_token')) {
        await refreshProfile();
      }
      if (!cancelled) setAuthReady(true);
    }
    boot();
    return () => { cancelled = true; };
  }, [refreshProfile]);

  return (
    <AuthContext.Provider
      value={{ user, setUser, login, logout, refreshProfile, authReady, home: homeForUser(user), isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

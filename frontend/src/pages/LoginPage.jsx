import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import { homeForUser } from '../utils/roles';
import Navbar from '../components/Navbar';
import '../styles/Auth.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      const payload = data?.data || data;
      const loggedUser = payload?.user || { email, first_name: email.split('@')[0] };
      login(
        loggedUser,
        payload?.access_token || data.access_token,
        payload?.refresh_token || data.refresh_token
      );
      // Role decides the landing: USER → user dashboard, ORGANIZER → organizer
      // dashboard, ADMIN → admin dashboard. A saved `from` only wins when it
      // matches the user's role area (or is a public page).
      const fromPath = location.state?.from?.pathname || '/';
      const role = String(loggedUser?.account_type || (loggedUser?.roles?.[0]) || 'user').toLowerCase();
      const roleArea = role === 'admin' ? '/admin' : role === 'organizer' ? '/organizer' : '/user';
      const target = fromPath === '/' || fromPath.startsWith(roleArea) || (!fromPath.startsWith('/admin') && !fromPath.startsWith('/organizer') && !fromPath.startsWith('/user'))
        ? fromPath
        : homeForUser(loggedUser);
      navigate(target, { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed. Check your email/password or whether the server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="auth-container">
          <h1>Log In</h1>
          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="form-error" role="alert">{error}</div>}
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>
          <p className="auth-switch">
            Don't have an account? <Link to="/register">Sign Up</Link>
          </p>
        </div>
      </main>
    </>
  );
}

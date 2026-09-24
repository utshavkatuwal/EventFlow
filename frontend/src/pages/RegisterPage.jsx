import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import { homeForUser } from '../utils/roles';
import Navbar from '../components/Navbar';
import '../styles/Auth.css';

export default function RegisterPage() {
  const [accountType, setAccountType] = useState('user');
  const [form, setForm] = useState({
    email: '', username: '', password: '', confirm_password: '',
    first_name: '', last_name: '', phone: '',
    organization_name: '', description: '', verification_info: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setNotice('');
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      const isOrg = accountType === 'organizer';
      const endpoint = isOrg ? '/auth/organizer/register' : '/auth/register';
      const full_name = `${form.first_name} ${form.last_name}`.trim();
      const payload = isOrg
        ? {
            full_name, first_name: form.first_name, last_name: form.last_name,
            email: form.email, phone: form.phone,
            password: form.password, confirm_password: form.confirm_password,
            organization_name: form.organization_name,
            description: form.description, verification_info: form.verification_info,
          }
        : {
            full_name, first_name: form.first_name, last_name: form.last_name,
            email: form.email, username: form.username, phone: form.phone,
            password: form.password, confirm_password: form.confirm_password,
          };
      const data = await apiFetch(endpoint, { method: 'POST', body: JSON.stringify(payload) });
      const res = data?.data || data;
      const newUser = res?.user || form;
      login(newUser, res?.access_token || data.access_token, res?.refresh_token || data.refresh_token);
      if (isOrg) {
        setNotice('Your organizer account is currently under review. You can log in, but publishing unlocks after approval.');
        setTimeout(() => navigate(homeForUser(newUser)), 1200);
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="auth-container">
          <h1>Sign Up</h1>
          <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 16 }}>
            {['user', 'organizer'].map((t) => (
              <button
                key={t}
                type="button"
                className={`dchip ${accountType === t ? 'on' : ''}`}
                onClick={() => setAccountType(t)}
              >
                {t === 'user' ? 'User' : 'Organizer'}
              </button>
            ))}
          </div>
          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="form-error" role="alert">{error}</div>}
            {notice && <div className="form-success" role="status">{notice}</div>}
            <div className="form-group">
              <label htmlFor="first_name">Full name</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <input id="first_name" name="first_name" type="text" placeholder="First" value={form.first_name} onChange={handleChange} />
                <input id="last_name" name="last_name" type="text" placeholder="Last" value={form.last_name} onChange={handleChange} />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
            </div>
            {accountType === 'user' && (
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input id="username" name="username" type="text" value={form.username} onChange={handleChange} required />
              </div>
            )}
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input id="phone" name="phone" type="tel" value={form.phone} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required minLength={6} />
            </div>
            <div className="form-group">
              <label htmlFor="confirm_password">Confirm password</label>
              <input id="confirm_password" name="confirm_password" type="password" value={form.confirm_password} onChange={handleChange} required minLength={6} />
            </div>
            {accountType === 'organizer' && (
              <>
                <div className="form-group">
                  <label htmlFor="organization_name">Organizer / business name</label>
                  <input id="organization_name" name="organization_name" type="text" value={form.organization_name} onChange={handleChange} required minLength={2} />
                </div>
                <div className="form-group">
                  <label htmlFor="description">Organizer description</label>
                  <input id="description" name="description" type="text" placeholder="What do you organize?" value={form.description} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label htmlFor="verification_info">Verification information</label>
                  <input id="verification_info" name="verification_info" type="text" placeholder="Registration no., PAN, website…" value={form.verification_info} onChange={handleChange} />
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  Document upload happens on your organizer dashboard after signup.
                </p>
              </>
            )}
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Creating account...' : accountType === 'organizer' ? 'Submit application' : 'Sign Up'}
            </button>
          </form>
          <p className="auth-switch">
            Already have an account? <Link to="/login">Log In</Link>
          </p>
        </div>
      </main>
    </>
  );
}

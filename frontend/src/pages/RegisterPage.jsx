import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import '../styles/Auth.css';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', username: '', password: '', first_name: '', last_name: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      login(form, data.access_token);
      navigate('/');
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
          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="form-error" role="alert">{error}</div>}
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <input id="first_name" name="first_name" type="text" value={form.first_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <input id="last_name" name="last_name" type="text" value={form.last_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input id="username" name="username" type="text" value={form.username} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required minLength={6} />
            </div>
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input id="phone" name="phone" type="tel" value={form.phone} onChange={handleChange} />
            </div>
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Creating account...' : 'Sign Up'}
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

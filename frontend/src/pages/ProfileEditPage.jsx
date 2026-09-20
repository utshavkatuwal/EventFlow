import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './ProfileEdit.css';

export default function ProfileEditPage() {
  const { user, login } = useAuth();
  const [form, setForm] = useState({ first_name: '', last_name: '', phone: '', avatar_url: '' });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        avatar_url: user.avatar_url || '',
      });
    }
  }, [user]);

  const handleSave = async () => {
    if (!user) return;
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/users/me', {
        method: 'PATCH',
        body: JSON.stringify(form),
      });
      login(data.data, null);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError(e.message || 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <p>Please log in.</p>;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Edit Profile</h1>

        {saved && <div className="form-success">Profile updated successfully!</div>}
        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="profile-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <input id="first_name" type="text" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <input id="last_name" type="text" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input id="phone" type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>

          <div className="form-group">
            <label htmlFor="avatar_url">Avatar URL</label>
            <input id="avatar_url" type="url" value={form.avatar_url} onChange={(e) => setForm({ ...form, avatar_url: e.target.value })} placeholder="https://..." />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </button>
        </form>
      </main>
    </>
  );
}
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/Profile.css';

export default function ProfilePage() {
  const { user, login, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ first_name: '', last_name: '', phone: '' });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/users/me');
        setProfile(data);
        setForm({
          first_name: data?.first_name || '',
          last_name: data?.last_name || '',
          phone: data?.phone || '',
        });
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSave = async () => {
    try {
      const data = await apiFetch('/users/me', {
        method: 'PATCH',
        body: JSON.stringify(form),
      });
      login(data, null);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      alert(e.message || 'Save failed');
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">My Profile</h1>

        <div className="profile-card">
          <div className="profile-avatar">
            {(profile?.first_name || profile?.username || 'U').charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h2>{profile?.first_name} {profile?.last_name}</h2>
            <p>{profile?.email}</p>
            <p>{profile?.phone || 'No phone'}</p>
            <p className="role-badge">{profile?.role || 'User'}</p>
          </div>
        </div>

        <div className="profile-form">
          <h3>Edit Profile</h3>
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <button className="btn btn-primary" onClick={handleSave}>
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </main>
    </>
  );
}

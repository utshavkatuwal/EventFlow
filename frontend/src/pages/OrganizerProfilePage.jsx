import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './OrganizerProfile.css';

export default function OrganizerProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ organization_name: '', description: '', website: '', phone: '', address: '', city: '' });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/profile');
        if (data?.data) {
          setProfile(data.data);
          setForm({
            organization_name: data.data.organization_name || '',
            description: data.data.description || '',
            website: data.data.website || '',
            phone: data.data.phone || '',
            address: data.data.address || '',
            city: data.data.city || '',
          });
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setError('');
    try {
      await apiFetch('/organizer/profile', {
        method: 'PATCH',
        body: JSON.stringify(form),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError(e.message || 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Organizer Profile</h1>

        {saved && <div className="form-success">Profile updated successfully!</div>}
        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="profile-form">
          <div className="form-group">
            <label htmlFor="organization_name">Organization Name</label>
            <input id="organization_name" type="text" value={form.organization_name} onChange={(e) => setForm({ ...form, organization_name: e.target.value })} required />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea id="description" rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="website">Website</label>
              <input id="website" type="url" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} placeholder="https://..." />
            </div>
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input id="phone" type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="address">Address</label>
              <input id="address" type="text" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            </div>
            <div className="form-group">
              <label htmlFor="city">City</label>
              <input id="city" type="text" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </button>
        </form>
      </main>
    </>
  );
}
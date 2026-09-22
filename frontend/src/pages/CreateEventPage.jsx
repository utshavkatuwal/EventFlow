import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import '../styles/CreateEvent.css';

const CATEGORIES = [
  'Technology', 'Education', 'Business', 'Music', 'Sports',
  'Gaming', 'Arts', 'Career', 'Workshop', 'Conference', 'Community', 'Other',
];
const STATUSES = ['DRAFT', 'PENDING_REVIEW', 'APPROVED', 'PUBLISHED'];

export default function CreateEventPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '', category_id: '', start_date: '', end_date: '',
    short_description: '', full_description: '', venue: '',
    city: '', address: '', max_capacity: '100', price_min: '0',
    status: 'DRAFT',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await apiFetch('/events', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          category_id: form.category_id ? parseInt(form.category_id) : undefined,
          max_capacity: parseInt(form.max_capacity),
          price_min: parseFloat(form.price_min),
          start_date: form.start_date ? new Date(form.start_date) : undefined,
          end_date: form.end_date ? new Date(form.end_date) : undefined,
        }),
      });
      setSuccess(true);
      setTimeout(() => navigate('/organizer/dashboard'), 2000);
    } catch (e) {
      setError(e.message || 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <p>Please log in to create events.</p>;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Create Event</h1>

        {success && <div className="form-success">Event created successfully! Redirecting...</div>}
        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={handleSubmit} className="create-event-form">
          <div className="form-group">
            <label htmlFor="title">Event Title *</label>
            <input id="title" name="title" type="text" required value={form.title} onChange={handleChange} />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category_id">Category</label>
              <select id="category_id" name="category_id" value={form.category_id} onChange={handleChange}>
                <option value="">Select Category</option>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select id="status" name="status" value={form.status} onChange={handleChange}>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start_date">Start Date *</label>
              <input id="start_date" name="start_date" type="date" required value={form.start_date} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="end_date">End Date</label>
              <input id="end_date" name="end_date" type="date" value={form.end_date} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="short_description">Short Description</label>
            <textarea id="short_description" name="short_description" rows={3} value={form.short_description} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="full_description">Full Description</label>
            <textarea id="full_description" name="full_description" rows={5} value={form.full_description} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="venue">Venue</label>
            <input id="venue" name="venue" type="text" value={form.venue} onChange={handleChange} />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="city">City</label>
              <input id="city" name="city" type="text" value={form.city} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="address">Address</label>
              <input id="address" name="address" type="text" value={form.address} onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="max_capacity">Max Capacity</label>
              <input id="max_capacity" name="max_capacity" type="number" min="1" value={form.max_capacity} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="price_min">Min Price (Rs.)</label>
              <input id="price_min" name="price_min" type="number" min="0" step="0.01" value={form.price_min} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? 'Creating...' : 'Create Event'}
          </button>
        </form>
      </main>
    </>
  );
}

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch, apiUpload } from '../services/api';
import Navbar from '../components/Navbar';
import '../styles/CreateEvent.css';

export default function CreateEventPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [verification, setVerification] = useState(null);
  const [form, setForm] = useState({
    title: '', category_id: '', start_date: '', end_date: '',
    short_description: '', full_description: '', venue: '',
    city: '', address: '', max_capacity: '100', price_min: '0',
    cover_image_url: '', video_url: '',
  });
  const [ticketTypes, setTicketTypes] = useState([{ name: 'General', price: '0', capacity: '100' }]);
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreview, setCoverPreview] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [uploading, setUploading] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    apiFetch('/categories').then((d) => setCategories(d.items || d.data || [])).catch(() => null);
    apiFetch('/organizer-applications/me')
      .then((d) => setVerification(d?.data || null))
      .catch(() => null);
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const setType = (i, field, value) =>
    setTicketTypes(ticketTypes.map((t, j) => (j === i ? { ...t, [field]: value } : t)));

  const uploadMedia = async (file, kind) => {
    const fd = new FormData();
    fd.append('file', file);
    const res = await apiUpload(`/events/upload?kind=${kind}`, fd);
    return res?.data?.url;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const types = ticketTypes
      .filter((t) => t.name.trim())
      .map((t) => ({ name: t.name.trim(), price: parseFloat(t.price) || 0, capacity: parseInt(t.capacity) || 0 }));
    if (types.length === 0) {
      setError('Add at least one ticket type.');
      return;
    }
    if (types.some((t) => t.capacity < 1)) {
      setError('Each ticket type needs capacity of at least 1.');
      return;
    }
    setLoading(true);
    try {
      // Upload chosen files first; fall back to the pasted URLs.
      let coverUrl = form.cover_image_url.trim() || undefined;
      let videoUrl = form.video_url?.trim() || undefined;
      if (coverFile) {
        setUploading('Uploading photo…');
        coverUrl = await uploadMedia(coverFile, 'cover');
      }
      if (videoFile) {
        setUploading('Uploading movie…');
        videoUrl = await uploadMedia(videoFile, 'video');
      }
      setUploading('');
      await apiFetch('/events', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          cover_image_url: coverUrl,
          video_url: videoUrl,
          ticket_types: types,
          category_id: form.category_id ? parseInt(form.category_id) : undefined,
          max_capacity: parseInt(form.max_capacity),
          price_min: Math.min(...types.map((t) => t.price)),
          start_date: form.start_date ? new Date(form.start_date).toISOString() : undefined,
          end_date: form.end_date ? new Date(form.end_date).toISOString() : undefined,
        }),
      });
      setSuccess(true);
      setTimeout(() => navigate('/organizer/dashboard'), 2000);
    } catch (e) {
      setError(e.message || 'Failed to create event');
    } finally {
      setLoading(false);
      setUploading('');
    }
  };

  if (!user) return <p>Please log in to create events.</p>;

  const status = verification?.verification_status || user?.organizer?.verification_status;
  const blocked = status && status !== 'APPROVED';

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Create Event</h1>

        {blocked && (
          <div className="card glass-secondary" style={{ padding: 18, marginBottom: 18, borderLeft: '3px solid rgba(255,255,255,0.5)' }}>
            <b>Your organizer account is currently under review.</b>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem' }}>
              You can create and save draft events now — publishing unlocks after admin approval.
            </p>
          </div>
        )}
        {success && <div className="form-success">Event created as draft! Redirecting...</div>}
        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={handleSubmit} className="create-event-form">
          <div className="form-group">
            <label htmlFor="title">Event Title *</label>
            <input id="title" name="title" type="text" required value={form.title} onChange={handleChange} />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category_id">Category *</label>
              <select id="category_id" name="category_id" value={form.category_id} onChange={handleChange} required>
                <option value="">Select Category</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="start_date">Start Date *</label>
              <input id="start_date" name="start_date" type="datetime-local" required value={form.start_date} onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="end_date">End Date</label>
              <input id="end_date" name="end_date" type="datetime-local" value={form.end_date} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="venue">Venue</label>
              <input id="venue" name="venue" type="text" value={form.venue} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="cover_image_url">Cover photo — upload file or paste URL</label>
            <input
              id="cover_file" type="file" accept=".jpg,.jpeg,.png,.webp"
              onChange={(e) => {
                const f = e.target.files?.[0] || null;
                setCoverFile(f);
                setCoverPreview(f ? URL.createObjectURL(f) : '');
              }}
            />
            <input id="cover_image_url" name="cover_image_url" type="url" placeholder="https://… (optional if uploading)" value={form.cover_image_url} onChange={handleChange} style={{ marginTop: 8 }} />
          </div>

          {(coverPreview || form.cover_image_url) && (
            <div className="form-group">
              <img src={coverPreview || form.cover_image_url} alt="Cover preview" style={{ width: '100%', maxHeight: 220, objectFit: 'cover', borderRadius: 14 }}
                onError={(e) => { e.target.style.display = 'none'; }} />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="video_file">Movie / trailer — upload file or paste URL</label>
            <input
              id="video_file" type="file" accept=".mp4,.webm,.mov"
              onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
            />
            <input id="video_url" name="video_url" type="url" placeholder="https://… (optional if uploading)" value={form.video_url} onChange={handleChange} style={{ marginTop: 8 }} />
            {videoFile && <small className="muted">Selected: {videoFile.name} ({Math.round(videoFile.size / 1048576)} MB)</small>}
          </div>

          <div className="form-group">
            <label htmlFor="short_description">Short Description</label>
            <textarea id="short_description" name="short_description" rows={3} value={form.short_description} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="full_description">Full Description</label>
            <textarea id="full_description" name="full_description" rows={5} value={form.full_description} onChange={handleChange} />
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
              <input id="price_min" name="price_min" type="number" min="0" step="0.01" value={Math.min(...ticketTypes.map((t) => parseFloat(t.price) || 0))} readOnly />
            </div>
          </div>

          <div className="form-group">
            <label>Ticket types</label>
            {ticketTypes.map((t, i) => (
              <div key={i} className="form-row" style={{ marginBottom: 8 }}>
                <div className="form-group" style={{ flex: 2 }}>
                  <input placeholder="Name (e.g. General, VIP)" value={t.name} onChange={(e) => setType(i, 'name', e.target.value)} aria-label="Ticket name" />
                </div>
                <div className="form-group">
                  <input type="number" min="0" step="0.01" placeholder="Price Rs." value={t.price} onChange={(e) => setType(i, 'price', e.target.value)} aria-label="Ticket price" />
                </div>
                <div className="form-group">
                  <input type="number" min="1" placeholder="Seats" value={t.capacity} onChange={(e) => setType(i, 'capacity', e.target.value)} aria-label="Ticket capacity" />
                </div>
                {ticketTypes.length > 1 && (
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setTicketTypes(ticketTypes.filter((_, j) => j !== i))}>×</button>
                )}
              </div>
            ))}
            {ticketTypes.length < 10 && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTicketTypes([...ticketTypes, { name: '', price: '0', capacity: '50' }])}>
                + Add ticket type
              </button>
            )}
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {uploading || (loading ? 'Creating...' : 'Save as draft')}
          </button>
        </form>
      </main>
    </>
  );
}

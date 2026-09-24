import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch, apiUpload } from '../services/api';
import { getEventImageUrl } from '../utils/images.js';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/Dashboard.css';

function VerificationBanner({ status, reason, onResubmit }) {
  const [form, setForm] = useState({ organization_name: '', description: '', verification_info: '' });
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);

  if (status === 'APPROVED') return null;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setMsg('');
    try {
      await apiFetch('/organizer-applications', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      if (file) {
        const fd = new FormData();
        fd.append('file', file);
        await apiUpload('/organizer-applications/me/documents', fd);
      }
      setMsg('Application resubmitted. Your organizer account is currently under review.');
      onResubmit?.();
    } catch (err) {
      setMsg(err.message || 'Resubmission failed');
    } finally {
      setBusy(false);
    }
  };

  const uploadOnly = async () => {
    if (!file) return;
    setBusy(true);
    setMsg('');
    try {
      const fd = new FormData();
      fd.append('file', file);
      await apiUpload('/organizer-applications/me/documents', fd);
      setMsg('Document uploaded.');
      onResubmit?.();
    } catch (err) {
      setMsg(err.message || 'Upload failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card glass-secondary" style={{ padding: 22, marginBottom: 22, borderLeft: '3px solid rgba(255,255,255,0.5)' }}>
      {status === 'REJECTED' ? (
        <>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 6 }}>Application rejected</h2>
          <p style={{ color: 'var(--error)', fontSize: '0.88rem', marginBottom: 12 }}>
            Reason: {reason || 'Not specified'}
          </p>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: 12 }}>
            Update your details and resubmit below. Uploading a new document also re-opens review.
          </p>
        </>
      ) : (
        <>
          <h2 style={{ fontSize: '1.1rem', marginBottom: 6 }}>Your organizer account is currently under review.</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: 12 }}>
            You can log in and explore, but event publishing unlocks after admin approval.
            You can upload verification documents below to speed things up.
          </p>
        </>
      )}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 12 }}>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button type="button" className="btn btn-secondary btn-sm" disabled={!file || busy} onClick={uploadOnly}>
          Upload document
        </button>
      </div>
      {status === 'REJECTED' && (
        <form onSubmit={submit} style={{ display: 'grid', gap: 10, marginTop: 8 }}>
          <input placeholder="Organization / business name" value={form.organization_name} onChange={(e) => setForm({ ...form, organization_name: e.target.value })} required />
          <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <input placeholder="Verification info (reg. no., PAN…)" value={form.verification_info} onChange={(e) => setForm({ ...form, verification_info: e.target.value })} />
          <button type="submit" className="btn btn-primary btn-sm" disabled={busy}>Resubmit application</button>
        </form>
      )}
      {msg && <p style={{ marginTop: 10, fontSize: '0.84rem' }}>{msg}</p>}
    </div>
  );
}

export default function OrganizerDashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [registrations, setRegistrations] = useState([]);
  const [verification, setVerification] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadVerification = async () => {
    try {
      const v = await apiFetch('/organizer-applications/me');
      setVerification(v?.data || null);
    } catch {
      setVerification(null);
    }
  };

  useEffect(() => {
    async function load() {
      try {
        const [s, e, r] = await Promise.all([
          apiFetch('/organizer/stats'),
          apiFetch('/organizer/events'),
          apiFetch('/organizer/registrations'),
        ]);
        setStats(s?.data || null);
        setEvents(e?.items || []);
        setRegistrations(r?.items || []);
        await loadVerification();
      } catch (e) {
        console.error(e);
        setError(e.message || 'Unable to connect to server.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Loading />;
  const status = verification?.verification_status || user?.organizer?.verification_status || 'UNDER_REVIEW';

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Organizer Dashboard</h1>

        {error && <div className="form-error" role="alert" style={{ marginBottom: 16 }}>{error}</div>}

        <VerificationBanner status={status} reason={verification?.rejection_reason || user?.organizer?.rejection_reason} onResubmit={loadVerification} />

        <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 18 }}>
          <Link to="/organizer/create-event" className="dchip">+ Create event</Link>
          <Link to="/organizer/my-events" className="dchip">My events</Link>
          <Link to="/organizer/checkin" className="dchip">Scan tickets</Link>
          <Link to="/organizer/registrations" className="dchip">Attendees</Link>
          <Link to="/organizer/analytics" className="dchip">Sales & wallet</Link>
        </div>

        <div className="dashboard-stats">
          <div className="stat"><span className="stat-number">{stats?.total_events || 0}</span><span className="stat-label">Total Events</span></div>
          <div className="stat"><span className="stat-number">{stats?.published_events || 0}</span><span className="stat-label">Published</span></div>
          <div className="stat"><span className="stat-number">{stats?.total_registrations || 0}</span><span className="stat-label">Registrations</span></div>
          <div className="stat"><span className="stat-number">{stats?.checkin_percentage || 0}%</span><span className="stat-label">Check-in Rate</span></div>
        </div>

        <section className="dashboard-section">
          <h2>My Events</h2>
          {events && events.length === 0 ? (
            <p className="empty-state">Create your first event to start managing registrations.</p>
          ) : (
            <div className="events-grid">
              {events?.map((ev) => (
                <Link key={ev.id} to={`/events/${ev.id}`} className="dashboard-event-card">
                  <div className="dashboard-event-image">
                    <img
                      src={getEventImageUrl(ev)}
                      alt={ev.title || 'Event'}
                      loading="lazy"
                      width="640"
                      height="160"
                      onError={(e) => {
                        e.target.src = getEventImageUrl({ ...ev, cover_image_url: null });
                      }}
                    />
                  </div>
                  <h3>{ev.title}</h3>
                  <span className={`status-badge status-${ev.status.toLowerCase().replace('_','-')}`}>{ev.status}</span>
                  <p style={{fontSize:'var(--fs-sm)', color:'var(--text-secondary)', marginTop:'4px'}}>{ev.start_date?.slice(0, 10)}</p>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Recent Registrations</h2>
          {registrations && registrations.length === 0 ? (
            <p className="empty-state">No registrations yet.</p>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr><th>Event</th><th>Attendee</th><th>Ticket</th><th>Date</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {registrations?.map((reg) => (
                    <tr key={reg.id}>
                      <td>{reg.event_title || '-'}</td>
                      <td>{reg.user_name || '-'}</td>
                      <td>{reg.ticket_type_name || '-'}</td>
                      <td>{reg.registration_date?.slice(0, 10)}</td>
                      <td>{reg.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </>
  );
}

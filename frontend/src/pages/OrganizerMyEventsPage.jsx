import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/OrganizerMyEvents.css';
import SimpleEventCard from '../components/SimpleEventCard';

const TABS = ['UPCOMING', 'ONGOING', 'ENDED', 'CANCELLED'];

export default function OrganizerMyEventsPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState(null);
  const [tab, setTab] = useState('UPCOMING');
  const [loading, setLoading] = useState(true);
  const [approved, setApproved] = useState(true);
  const [actionError, setActionError] = useState('');

  useEffect(() => {
    apiFetch('/organizer-applications/me')
      .then((d) => setApproved(d?.data?.verification_status === 'APPROVED'))
      .catch(() => setApproved(user?.organizer?.verification_status === 'APPROVED'));
  }, []);

  const load = async (lifecycle) => {
    setLoading(true);
    try {
      const data = await apiFetch(`/organizer/events?lifecycle=${lifecycle}`);
      setEvents(data?.items || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(tab); }, [tab]);

  const publish = async (id) => {
    try {
      setActionError('');
      await apiFetch(`/events/${id}/publish`, { method: 'PATCH' });
      load(tab);
    } catch (e) { setActionError(e.message || 'Publish failed'); }
  };

  const cancel = async (id) => {
    if (!window.confirm('Cancel this event? New purchases will be blocked; history is preserved.')) return;
    try {
      setActionError('');
      await apiFetch(`/events/${id}/cancel`, { method: 'PATCH' });
      load(tab);
    } catch (e) { setActionError(e.message || 'Cancel failed'); }
  };

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="organizer-events-header">
          <h1>My Events</h1>
          <Link to="/organizer/create-event" className="btn btn-primary btn-sm">+ New event</Link>
        </div>

        <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 16 }}>
          {TABS.map((t) => (
            <button key={t} type="button" className={`dchip ${tab === t ? 'on' : ''}`} onClick={() => setTab(t)}>
              {t.charAt(0) + t.slice(1).toLowerCase()}
            </button>
          ))}
        </div>

        {!approved && (
          <div className="card glass-secondary" style={{ padding: 16, marginBottom: 16 }}>
            <b>Your organizer account is currently under review.</b>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem' }}>
              Drafts save normally — publishing unlocks after admin approval.
            </p>
          </div>
        )}
        {actionError && <div className="form-error" role="alert" style={{ marginBottom: 16 }}>{actionError}</div>}

        {events && events.length === 0 ? (
          <p className="empty-state">No {tab.toLowerCase()} events.</p>
        ) : (
          <div className="events-grid">
            {events?.map((ev) => (
              <div key={ev.id}>
                <SimpleEventCard event={ev} />
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 6 }}>
                  Status: {ev.status} · {ev.lifecycle || ''}{ev.start_date ? ` · Starts ${String(ev.start_date).slice(0, 10)}` : ''}
                </p>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  {ev.status === 'DRAFT' && (
                    <button className="btn btn-primary btn-sm" onClick={() => publish(ev.id)}>Publish</button>
                  )}
                  {ev.status !== 'CANCELLED' && (
                    <button className="btn btn-secondary btn-sm" onClick={() => cancel(ev.id)}>Cancel</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}

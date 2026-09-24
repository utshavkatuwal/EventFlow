import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import { getEventImageUrl } from '../utils/images.js';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/Dashboard.css';

export default function UserDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [upcoming, setUpcoming] = useState([]);
  const [past, setPast] = useState([]);
  const [savedEvents, setSavedEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [s, u, p, sv] = await Promise.all([
          apiFetch('/user/stats'),
          apiFetch('/user/upcoming'),
          apiFetch('/user/past'),
          apiFetch('/user/saved'),
        ]);
        setStats(s?.data || null);
        setUpcoming(u?.items || []);
        setPast(p?.items || []);
        setSavedEvents(sv?.items || []);
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

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">My Dashboard</h1>

        {error && <div className="form-error" role="alert" style={{ marginBottom: 16 }}>{error}</div>}

        <div className="dashboard-stats">
          <div className="stat"><span className="stat-number">{stats?.total_registrations || 0}</span><span className="stat-label">Registrations</span></div>
          <div className="stat"><span className="stat-number">{stats?.upcoming || 0}</span><span className="stat-label">Upcoming</span></div>
          <div className="stat"><span className="stat-number">{stats?.saved || 0}</span><span className="stat-label">Saved</span></div>
          <div className="stat"><Link to="/user/tickets" className="stat-label" style={{ textDecoration: 'underline' }}>My Tickets →</Link></div>
        </div>

        <section className="dashboard-section">
          <h2>Upcoming Events</h2>
          {upcoming && upcoming.length === 0 ? (
            <p className="empty-state">You have not registered for an event yet.</p>
          ) : (
            <div className="events-grid">
              {upcoming?.map((ev) => (
                <EventCard key={ev.id} event={ev} />
              ))}
            </div>
          )}
        </section>

        {past && past.length > 0 && (
          <section className="dashboard-section">
            <h2>Past Events</h2>
            <div className="events-grid">
              {past.map((ev) => (
                <EventCard key={ev.id} event={ev} />
              ))}
            </div>
          </section>
        )}

        <section className="dashboard-section">
          <h2>Saved Events</h2>
          {savedEvents && savedEvents.length === 0 ? (
            <p className="empty-state">Your saved events will appear here.</p>
          ) : (
            <div className="events-grid">
              {savedEvents?.map((ev) => (
                <EventCard key={ev.id} event={ev} />
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}

function EventCard({ event }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };
  return (
    <article className="event-card">
      <div className="event-card-image">
        <img
          src={getEventImageUrl(event)}
          alt={event.title || 'Event'}
          loading="lazy"
          width="640"
          height="400"
          onError={(e) => {
            e.target.src = getEventImageUrl({ ...event, cover_image_url: null });
          }}
        />
      </div>
      <div className="event-card-body">
        <span className="event-card-category">{event.category_name || 'Event'}</span>
        <h3 className="event-card-title">
          <Link to={`/events/${event.id}`}>{event.title}</Link>
        </h3>
        <div className="event-card-meta">
          <span>{formatDate(event.start_date)}</span>
          <span>{event.city || ''}</span>
        </div>
      </div>
    </article>
  );
}

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/Dashboard.css';

export default function OrganizerDashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState(null);
  const [registrations, setRegistrations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const s = await apiFetch('/organizer/stats').catch(() => null);
        const e = await apiFetch('/organizer/events').catch(() => null);
        const r = await apiFetch('/organizer/registrations').catch(() => null);
        setStats(s);
        setEvents(e);
        setRegistrations(r);
      } catch (e) {
        console.error(e);
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
        <h1 className="dashboard-title">Organizer Dashboard</h1>

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
                  {ev.cover_image_url && (
                    <img src={ev.cover_image_url} alt={ev.title} style={{width:'100%', height:'160px', objectFit:'cover', borderRadius:'8px', marginBottom:'12px'}} />
                  )}
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

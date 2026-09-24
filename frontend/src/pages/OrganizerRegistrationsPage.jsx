import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/OrganizerRegistrations.css';

export default function OrganizerRegistrationsPage() {
  const [events, setEvents] = useState([]);
  const [eventId, setEventId] = useState('');
  const [attendees, setAttendees] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/events');
        const items = data?.items || [];
        setEvents(items);
        if (items.length > 0) setEventId(String(items[0].id));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  useEffect(() => {
    if (!eventId) return;
    async function loadAttendees() {
      try {
        const data = await apiFetch(`/organizer/events/${eventId}/attendees`);
        setAttendees(data?.data?.attendees || []);
        setStats(data?.data?.stats || null);
      } catch (e) {
        console.error(e);
        setAttendees([]);
      }
    }
    loadAttendees();
  }, [eventId]);

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Attendees</h1>

        <div className="form-group" style={{ maxWidth: 420, marginBottom: 16 }}>
          <label htmlFor="att-event">Event</label>
          <select id="att-event" value={eventId} onChange={(e) => setEventId(e.target.value)}>
            {events.map((ev) => (
              <option key={ev.id} value={ev.id}>{ev.title}</option>
            ))}
          </select>
        </div>

        {stats && (
          <div className="dashboard-stats">
            <div className="stat"><span className="stat-number">{stats.tickets_sold}</span><span className="stat-label">Tickets sold</span></div>
            <div className="stat"><span className="stat-number">{stats.tickets_remaining}</span><span className="stat-label">Remaining</span></div>
            <div className="stat"><span className="stat-number">{stats.attended}</span><span className="stat-label">Attended</span></div>
            <div className="stat"><span className="stat-number">{stats.not_attended}</span><span className="stat-label">Not attended</span></div>
            <div className="stat"><span className="stat-number">Rs. {Number(stats.revenue || 0).toLocaleString()}</span><span className="stat-label">Revenue</span></div>
          </div>
        )}

        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Attendee</th><th>Ticket ID</th><th>Registered</th><th>Payment</th><th>Attendance</th><th>Time</th></tr></thead>
            <tbody>
              {attendees?.map((r) => (
                <tr key={r.registration_id}>
                  <td>{r.attendee_name || '-'}</td>
                  <td><span className="monospace">{r.ticket_code || '-'}</span></td>
                  <td>{String(r.registration_date || '').slice(0, 10)}</td>
                  <td><span className={`status-badge status-${String(r.payment_status).toLowerCase()}`}>{r.payment_status}</span></td>
                  <td><span className={`status-badge status-${String(r.attendance_status).toLowerCase()}`}>{r.attendance_status}</span></td>
                  <td>{r.attendance_time ? new Date(r.attendance_time).toLocaleString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {attendees.length === 0 && <p className="empty-state">No attendees yet.</p>}
        </div>
      </main>
    </>
  );
}

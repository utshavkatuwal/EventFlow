import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/AdminEvents.css';
import SimpleEventCard from '../components/SimpleEventCard';

export default function AdminEventsPage() {
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/admin/events');
        setEvents(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleApprove = async (eventId) => {
    try {
      await apiFetch(`/admin/events/${eventId}/approve`, { method: 'PATCH' });
      setEvents(events.map(e => e.id === eventId ? { ...e, status: 'APPROVED' } : e));
    } catch (e) {
      alert(e.message);
    }
  };

  const handleReject = async (eventId) => {
    try {
      await apiFetch(`/admin/events/${eventId}/reject`, { method: 'PATCH' });
      setEvents(events.map(e => e.id === eventId ? { ...e, status: 'REJECTED' } : e));
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Events Management</h1>

        <div className="admin-events-table">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Organizer</th>
                <th>Category</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {events?.map((ev) => (
                <tr key={ev.id}>
                  <td>{ev.title}</td>
                  <td>{ev.organizer_name || '-'}</td>
                  <td>{ev.category_name || '-'}</td>
                  <td><span className={`status-badge status-${ev.status.toLowerCase().replace('_','-')}`}>{ev.status}</span></td>
                  <td>{ev.start_date?.slice(0, 10)}</td>
                  <td>
                    {ev.status === 'PENDING_REVIEW' && (
                      <div className="action-buttons">
                        <button className="btn btn-success btn-sm" onClick={() => handleApprove(ev.id)}>Approve</button>
                        <button className="btn btn-error btn-sm" onClick={() => handleReject(ev.id)}>Reject</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
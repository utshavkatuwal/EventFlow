import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './Dashboard.css';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const s = await apiFetch('/admin/stats').catch(() => null);
        const e = await apiFetch('/admin/events').catch(() => null);
        setStats(s);
        setRecentEvents(e);
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
        <h1 className="dashboard-title">Admin Dashboard</h1>

        <div className="dashboard-stats">
          <div className="stat"><span className="stat-number">{stats?.total_users || 0}</span><span className="stat-label">Users</span></div>
          <div className="stat"><span className="stat-number">{stats?.total_organizers || 0}</span><span className="stat-label">Organizers</span></div>
          <div className="stat"><span className="stat-number">{stats?.total_events || 0}</span><span className="stat-label">Events</span></div>
          <div className="stat"><span className="stat-number">{stats?.pending_events || 0}</span><span className="stat-label">Pending</span></div>
        </div>

        <section className="dashboard-section">
          <h2>Events</h2>
          {recentEvents && recentEvents.length === 0 ? (
            <p className="empty-state">No events yet.</p>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr><th>Title</th><th>Organizer</th><th>Category</th><th>Status</th><th>Date</th></tr>
                </thead>
                <tbody>
                  {recentEvents?.map((ev) => (
                    <tr key={ev.id}>
                      <td>{ev.title}</td>
                      <td>{ev.organizer_name || '-'}</td>
                      <td>{ev.category_name || '-'}</td>
                      <td>{ev.status}</td>
                      <td>{ev.start_date?.slice(0, 10)}</td>
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

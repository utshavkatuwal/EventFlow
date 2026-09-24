import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/Dashboard.css';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState(null);
  const [settings, setSettings] = useState(null);
  const [editKey, setEditKey] = useState('');
  const [editVal, setEditVal] = useState('');
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [s, e, st] = await Promise.all([
          apiFetch('/admin/stats').catch(() => null),
          apiFetch('/admin/events').catch(() => null),
          apiFetch('/admin/settings').catch(() => null),
        ]);
        setStats(s?.data || null);
        setRecentEvents(e?.items || []);
        setSettings(st?.data || null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const saveSetting = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await apiFetch('/admin/settings', { method: 'PATCH', body: JSON.stringify({ key: editKey, value: Number(editVal) }) });
      setMsg(`${editKey} updated to ${editVal}`);
      const st = await apiFetch('/admin/settings').catch(() => null);
      setSettings(st?.data || null);
      setEditKey('');
      setEditVal('');
    } catch (err) {
      setMsg(err.message || 'Update failed');
    }
  };

  if (loading) return <Loading />;

  const cards = [
    ['Users', stats?.total_users], ['Organizers', stats?.total_organizers],
    ['Pending orgs', stats?.pending_organizers], ['Events', stats?.total_events],
    ['Active', stats?.active_events], ['Ended', stats?.ended_events],
    ['Tickets sold', stats?.tickets_sold], ['Attended', stats?.total_attendees],
    ['Volume Rs.', stats?.transaction_volume], ['Wallets avail Rs.', stats?.wallet_available_total],
    ['Wallets pend Rs.', stats?.wallet_pending_total], ['Pending payouts', stats?.pending_withdrawals],
  ];

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin Dashboard</h1>

        <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 18 }}>
          {[
            ['Organizers', '/admin/organizers'],
            ['Withdrawals', '/admin/withdrawals'],
            ['Events', '/admin/events'],
            ['Users', '/admin/users'],
            ['Reports', '/admin/reports'],
            ['Categories', '/admin/categories'],
          ].map(([label, to]) => (
            <Link key={to} to={to} className="dchip">{label} →</Link>
          ))}
        </div>

        <div className="dashboard-stats">
          {cards.map(([label, v]) => (
            <div className="stat" key={label}>
              <span className="stat-number">{v ?? 0}</span>
              <span className="stat-label">{label}</span>
            </div>
          ))}
        </div>

        <section className="dashboard-section">
          <h2>Platform settings</h2>
          <div className="table-container" style={{ marginBottom: 12 }}>
            <table className="data-table">
              <thead><tr><th>Key</th><th>Value</th></tr></thead>
              <tbody>
                {Object.entries(settings || {}).map(([k, v]) => (
                  <tr key={k}><td>{k}</td><td>{v}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <form onSubmit={saveSetting} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <select value={editKey} onChange={(e) => setEditKey(e.target.value)} required>
              <option value="">Select key</option>
              <option value="withdrawal_service_fee">withdrawal_service_fee</option>
              <option value="platform_ticket_fee">platform_ticket_fee</option>
              <option value="settlement_hold_days">settlement_hold_days</option>
            </select>
            <input type="number" step="any" placeholder="New value" value={editVal} onChange={(e) => setEditVal(e.target.value)} required />
            <button type="submit" className="btn btn-primary btn-sm">Save</button>
          </form>
          {msg && <p style={{ marginTop: 8, fontSize: '0.86rem' }}>{msg}</p>}
        </section>

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
                  {recentEvents?.slice(0, 10).map((ev) => (
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

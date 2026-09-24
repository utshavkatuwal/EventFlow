import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/OrganizerAnalytics.css';

export default function OrganizerAnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [eventId, setEventId] = useState('');
  const [sales, setSales] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [withdrawals, setWithdrawals] = useState([]);
  const [wdForm, setWdForm] = useState({ provider: 'ESEWA', account_number: '', amount: '' });
  const [wdMsg, setWdMsg] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [s, e, w, wd] = await Promise.all([
          apiFetch('/organizer/stats').catch(() => null),
          apiFetch('/organizer/events').catch(() => null),
          apiFetch('/organizer/wallet').catch(() => null),
          apiFetch('/withdrawals/me').catch(() => null),
        ]);
        setStats(s?.data || null);
        const items = e?.items || [];
        setEvents(items);
        if (items.length > 0) setEventId(String(items[0].id));
        setWallet(w?.data || null);
        setWithdrawals(wd?.items || []);
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
    apiFetch(`/organizer/events/${eventId}/sales`)
      .then((d) => setSales(d?.data || null))
      .catch(() => setSales(null));
  }, [eventId]);

  if (loading) return <Loading />;

  const submitWithdrawal = async (e) => {
    e.preventDefault();
    setWdMsg('');
    try {
      const res = await apiFetch('/withdrawals', {
        method: 'POST',
        body: JSON.stringify({ ...wdForm, amount: parseFloat(wdForm.amount) }),
      });
      setWdMsg(`Requested Rs.${res?.data?.requested_amount} — you receive Rs.${res?.data?.payout_amount} after Rs.${res?.data?.service_fee} fee.`);
      setWdForm({ provider: 'ESEWA', account_number: '', amount: '' });
      const [w, wd] = await Promise.all([
        apiFetch('/organizer/wallet').catch(() => null),
        apiFetch('/withdrawals/me').catch(() => null),
      ]);
      setWallet(w?.data || null);
      setWithdrawals(wd?.items || []);
    } catch (err) {
      setWdMsg(err.message || 'Withdrawal failed');
    }
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Analytics</h1>

        <div className="dashboard-stats">
          <div className="stat"><span className="stat-number">{stats?.total_events || 0}</span><span className="stat-label">Total Events</span></div>
          <div className="stat"><span className="stat-number">{stats?.published_events || 0}</span><span className="stat-label">Published</span></div>
          <div className="stat"><span className="stat-number">{stats?.total_registrations || 0}</span><span className="stat-label">Registrations</span></div>
          <div className="stat"><span className="stat-number">{stats?.checkin_percentage || 0}%</span><span className="stat-label">Check-in Rate</span></div>
        </div>

        <section className="dashboard-section">
          <h2>Wallet</h2>
          <div className="dashboard-stats">
            <div className="stat"><span className="stat-number">Rs. {Number(wallet?.available_balance || 0).toLocaleString()}</span><span className="stat-label">Available Balance</span></div>
            <div className="stat"><span className="stat-number">Rs. {Number(wallet?.pending_balance || 0).toLocaleString()}</span><span className="stat-label">Pending settlement</span></div>
          </div>

          <div className="card glass-secondary" style={{ padding: 20, marginBottom: 16 }}>
            <h3 style={{ marginBottom: 10 }}>Withdraw</h3>
            <form onSubmit={submitWithdrawal} style={{ display: 'grid', gap: 10, maxWidth: 480 }}>
              <div style={{ display: 'flex', gap: 8 }}>
                {['ESEWA', 'KHALTI'].map((p) => (
                  <label key={p} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.86rem' }}>
                    <input type="radio" name="provider" checked={wdForm.provider === p} onChange={() => setWdForm({ ...wdForm, provider: p })} />
                    {p === 'ESEWA' ? 'eSewa' : 'Khalti'}
                  </label>
                ))}
              </div>
              <input
                placeholder="Wallet / phone number" value={wdForm.account_number}
                onChange={(e) => setWdForm({ ...wdForm, account_number: e.target.value })} required
              />
              <input
                type="number" min="1" step="0.01" placeholder="Amount (Rs.)" value={wdForm.amount}
                onChange={(e) => setWdForm({ ...wdForm, amount: e.target.value })} required
              />
              <button type="submit" className="btn btn-primary btn-md" style={{ justifySelf: 'start' }}>Request Withdrawal</button>
            </form>
            {wdMsg && <p style={{ marginTop: 10, fontSize: '0.86rem' }}>{wdMsg}</p>}
          </div>

          {withdrawals.length > 0 && (
            <div className="table-container" style={{ marginBottom: 16 }}>
              <table className="data-table">
                <thead><tr><th>Date</th><th>Method</th><th>Requested</th><th>Fee</th><th>Payout</th><th>Status</th><th>Reference</th></tr></thead>
                <tbody>
                  {withdrawals.map((w) => (
                    <tr key={w.id}>
                      <td>{String(w.created_at || '').slice(0, 10)}</td>
                      <td>{w.provider} · {w.account_number}</td>
                      <td>Rs. {Number(w.requested_amount || 0).toLocaleString()}</td>
                      <td>Rs. {Number(w.service_fee || 0).toLocaleString()}</td>
                      <td>Rs. {Number(w.payout_amount || 0).toLocaleString()}</td>
                      <td><span className={`status-badge status-${String(w.status).toLowerCase()}`}>{w.status}</span></td>
                      <td>{w.transaction_reference || w.admin_note || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {wallet?.transactions?.length > 0 && (
            <div className="table-container">
              <table className="data-table">
                <thead><tr><th>Type</th><th>Amount</th><th>Description</th><th>Date</th></tr></thead>
                <tbody>
                  {wallet.transactions.slice(0, 10).map((t) => (
                    <tr key={t.id}>
                      <td>{t.type}</td>
                      <td>Rs. {Number(t.amount || 0).toLocaleString()}</td>
                      <td>{t.description || '-'}</td>
                      <td>{String(t.created_at || '').slice(0, 10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Sales by event</h2>
          <div className="form-group" style={{ maxWidth: 420, marginBottom: 16 }}>
            <label htmlFor="sales-event">Event</label>
            <select id="sales-event" value={eventId} onChange={(e) => setEventId(e.target.value)}>
              {events.map((ev) => (
                <option key={ev.id} value={ev.id}>{ev.title}</option>
              ))}
            </select>
          </div>
          {sales && (
            <>
              <div className="dashboard-stats">
                <div className="stat"><span className="stat-number">Rs. {Number(sales.gross_revenue || 0).toLocaleString()}</span><span className="stat-label">Gross</span></div>
                <div className="stat"><span className="stat-number">Rs. {Number(sales.platform_fees || 0).toLocaleString()}</span><span className="stat-label">Platform fees</span></div>
                <div className="stat"><span className="stat-number">Rs. {Number(sales.net_earning || 0).toLocaleString()}</span><span className="stat-label">Net earning</span></div>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>Ticket type</th><th>Price</th><th>Sold</th><th>Remaining</th><th>Gross</th></tr></thead>
                  <tbody>
                    {sales.breakdown?.map((b, i) => (
                      <tr key={i}>
                        <td>{b.ticket_type}</td>
                        <td>Rs. {Number(b.price || 0).toLocaleString()}</td>
                        <td>{b.sold}</td>
                        <td>{b.remaining}</td>
                        <td>Rs. {Number(b.gross || 0).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      </main>
    </>
  );
}

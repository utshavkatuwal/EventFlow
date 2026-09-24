import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/AdminReports.css';

export default function AdminWithdrawalsPage() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState('PENDING');
  const [loading, setLoading] = useState(true);
  const [refMap, setRefMap] = useState({});
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async (status = filter) => {
    setLoading(true);
    setError('');
    try {
      const qs = status ? `?status=${encodeURIComponent(status)}` : '';
      const data = await apiFetch(`/withdrawals${qs}`);
      setItems(data?.items || []);
    } catch (e) {
      setError(e.message || 'Failed to load withdrawals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load('PENDING'); }, []);

  const act = async (id, action) => {
    setBusy(true);
    setError('');
    try {
      if (action === 'pay') {
        const reference = (refMap[id] || '').trim();
        if (!reference) throw new Error('Enter the manual transaction reference first');
        await apiFetch(`/withdrawals/${id}/pay`, {
          method: 'POST', body: JSON.stringify({ transaction_reference: reference }),
        });
      } else if (action === 'approve') {
        await apiFetch(`/withdrawals/${id}/approve`, { method: 'POST' });
      } else {
        const reason = (refMap[`${id}_note`] || '').trim();
        if (!reason) throw new Error('Enter a rejection reason first');
        await apiFetch(`/withdrawals/${id}/reject`, {
          method: 'POST', body: JSON.stringify({ admin_note: reason }),
        });
      }
      await load();
    } catch (e) {
      setError(e.message || 'Action failed');
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Pending Withdrawals</h1>

        <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 16 }}>
          {['PENDING', 'APPROVED', 'PAID', 'REJECTED', ''].map((s) => (
            <button key={s || 'all'} type="button" className={`dchip ${filter === s ? 'on' : ''}`}
              onClick={() => { setFilter(s); load(s); }}>
              {s || 'All'}
            </button>
          ))}
        </div>

        {error && <div className="form-error" role="alert" style={{ marginBottom: 12 }}>{error}</div>}

        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Organizer</th><th>Method</th><th>Requested</th><th>Fee</th><th>Payout</th><th>Date</th><th>Status</th><th>Manual payout</th></tr></thead>
            <tbody>
              {items.map((w) => (
                <tr key={w.id}>
                  <td><b>{w.organization_name}</b><br />{w.organizer_email}</td>
                  <td>{w.provider}<br />{w.account_number}</td>
                  <td>Rs. {Number(w.requested_amount || 0).toLocaleString()}</td>
                  <td>Rs. {Number(w.service_fee || 0).toLocaleString()}</td>
                  <td><b>Rs. {Number(w.payout_amount || 0).toLocaleString()}</b></td>
                  <td>{String(w.created_at || '').slice(0, 10)}</td>
                  <td>
                    <span className={`status-badge status-${String(w.status).toLowerCase()}`}>{w.status}</span>
                    {w.transaction_reference && <div style={{ fontSize: '0.75rem' }}>Ref: {w.transaction_reference}</div>}
                    {w.admin_note && <div style={{ fontSize: '0.75rem' }}>{w.admin_note}</div>}
                  </td>
                  <td>
                    {(w.status === 'PENDING' || w.status === 'APPROVED') ? (
                      <div style={{ display: 'grid', gap: 6, minWidth: 220 }}>
                        {w.status === 'PENDING' && (
                          <button className="btn btn-ghost btn-sm" disabled={busy} onClick={() => act(w.id, 'approve')}>Approve</button>
                        )}
                        <input
                          placeholder="Manual transaction reference"
                          value={refMap[w.id] || ''}
                          onChange={(e) => setRefMap({ ...refMap, [w.id]: e.target.value })}
                        />
                        <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => act(w.id, 'pay')}>
                          Confirm Manual Payment
                        </button>
                        <input
                          placeholder="Rejection reason"
                          value={refMap[`${w.id}_note`] || ''}
                          onChange={(e) => setRefMap({ ...refMap, [`${w.id}_note`]: e.target.value })}
                        />
                        <button className="btn btn-secondary btn-sm" disabled={busy} onClick={() => act(w.id, 'reject')}>Reject</button>
                      </div>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {items.length === 0 && <p className="empty-state">No withdrawals.</p>}
        </div>
      </main>
    </>
  );
}

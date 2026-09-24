import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import { API_BASE } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/AdminOrganizers.css';

export default function AdminOrganizersPage() {
  const [apps, setApps] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [rejectId, setRejectId] = useState(null);
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = async (status = filter) => {
    setLoading(true);
    setError('');
    try {
      const qs = status ? `?status=${encodeURIComponent(status)}` : '';
      const data = await apiFetch(`/organizer-applications${qs}`);
      setApps(data?.data || data?.items || []);
    } catch (e) {
      setError(e.message || 'Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(''); }, []);

  const review = async (id, action) => {
    if (action === 'REJECT' && !reason.trim()) {
      setError('Rejection reason is required');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await apiFetch(`/organizer-applications/${id}/review`, {
        method: 'POST',
        body: JSON.stringify({ action, rejection_reason: reason }),
      });
      setRejectId(null);
      setReason('');
      await load();
    } catch (e) {
      setError(e.message || 'Review failed');
    } finally {
      setBusy(false);
    }
  };

  const docUrl = (appId, docId) =>
    `${API_BASE}/organizer-applications/${appId}/documents/${docId}/file`;

  const authDownload = async (appId, doc) => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(docUrl(appId, doc.id), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.filename || 'document';
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Organizer Applications</h1>

        <div className="disc-chips" style={{ justifyContent: 'flex-start', padding: 0, marginBottom: 16 }}>
          {['', 'UNDER_REVIEW', 'APPROVED', 'REJECTED'].map((s) => (
            <button
              key={s || 'all'}
              type="button"
              className={`dchip ${filter === s ? 'on' : ''}`}
              onClick={() => { setFilter(s); load(s); }}
            >
              {s || 'All'}
            </button>
          ))}
        </div>

        {error && <div className="form-error" role="alert" style={{ marginBottom: 12 }}>{error}</div>}

        <div className="admin-organizers-table">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Organizer</th><th>Email / Phone</th><th>Business</th>
                  <th>Submitted</th><th>Status</th><th>Documents</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {apps.map((a) => (
                  <tr key={a.id}>
                    <td>{a.organizer_name}</td>
                    <td>{a.email || '-'}<br />{a.phone || ''}</td>
                    <td><b>{a.organization_name}</b><br />{a.verification_info || a.description || ''}</td>
                    <td>{String(a.submitted_at || '').slice(0, 10)}</td>
                    <td>
                      <span className={`status-badge status-${String(a.verification_status || '').toLowerCase()}`}>
                        {a.verification_status}
                      </span>
                      {a.verification_status === 'REJECTED' && a.rejection_reason && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--error)' }}>{a.rejection_reason}</div>
                      )}
                    </td>
                    <td>
                      {(a.documents || []).length === 0 && <span style={{ color: 'var(--text-muted)' }}>—</span>}
                      {(a.documents || []).map((d) => (
                        <div key={d.id}>
                          <button type="button" className="btn btn-ghost btn-sm" onClick={() => authDownload(a.id, d)}>
                            {d.filename} ({Math.round((d.file_size || 0) / 1024)}KB)
                          </button>
                        </div>
                      ))}
                    </td>
                    <td>
                      {a.verification_status !== 'APPROVED' && (
                        <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => review(a.id, 'APPROVE')}>
                          Approve
                        </button>
                      )}{' '}
                      {a.verification_status !== 'REJECTED' && (
                        <button className="btn btn-secondary btn-sm" disabled={busy} onClick={() => setRejectId(a.id)}>
                          Reject
                        </button>
                      )}
                      {rejectId === a.id && (
                        <div style={{ marginTop: 8, display: 'grid', gap: 6 }}>
                          <input
                            placeholder="Rejection reason (required)"
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                          />
                          <div style={{ display: 'flex', gap: 6 }}>
                            <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => review(a.id, 'REJECT')}>
                              Confirm
                            </button>
                            <button className="btn btn-ghost btn-sm" onClick={() => { setRejectId(null); setReason(''); }}>
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {apps.length === 0 && <p className="empty-state">No applications.</p>}
        </div>
      </main>
    </>
  );
}

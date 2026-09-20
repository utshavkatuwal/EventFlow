import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './AdminReports.css';

export default function AdminReportsPage() {
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/admin/reports');
        setReports(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleResolve = async (reportId) => {
    try {
      await apiFetch(`/admin/reports/${reportId}/resolve`, { method: 'PATCH' });
      setReports(reports.map(r => r.id === reportId ? { ...r, status: 'RESOLVED' } : r));
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Reports</h1>

        <div className="admin-reports-table">
          <table className="data-table">
            <thead>
              <tr><th>Type</th><th>Reference</th><th>Reason</th><th>Status</th><th>Date</th><th>Action</th></tr>
            </thead>
            <tbody>
              {reports?.map((r) => (
                <tr key={r.id}>
                  <td>{r.report_type}</td>
                  <td>{r.reference_type} #{r.reference_id}</td>
                  <td>{r.reason || '-'}</td>
                  <td><span className={`status-badge status-${r.status.toLowerCase()}`}>{r.status}</span></td>
                  <td>{r.created_at?.slice(0, 10)}</td>
                  <td>
                    {r.status === 'OPEN' && (
                      <button className="btn btn-primary btn-sm" onClick={() => handleResolve(r.id)}>Resolve</button>
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
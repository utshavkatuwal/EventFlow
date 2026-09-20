import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './AdminAuditLogs.css';

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/admin/audit-logs');
        setLogs(data?.items || []);
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
        <h1 className="dashboard-title">Admin - Audit Logs</h1>

        <div className="admin-audit-table">
          <table className="data-table">
            <thead>
              <tr><th>Action</th><th>Entity</th><th>ID</th><th>Admin</th><th>Details</th><th>Date</th></tr>
            </thead>
            <tbody>
              {logs?.map((log) => (
                <tr key={log.id}>
                  <td>{log.action}</td>
                  <td>{log.entity_type}</td>
                  <td>{log.entity_id || '-'}</td>
                  <td>{log.admin_name || '-'}</td>
                  <td><pre>{JSON.stringify(log.details, null, 2)}</pre></td>
                  <td>{log.created_at?.slice(0, 16)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './AdminOrganizers.css';

export default function AdminOrganizersPage() {
  const [organizers, setOrganizers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizers');
        setOrganizers(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleVerify = async (orgId) => {
    try {
      await apiFetch(`/organizers/${orgId}/verify`, { method: 'PATCH' });
      setOrganizers(organizers.map(o => o.id === orgId ? { ...o, is_verified: true } : o));
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Organizers</h1>

        <div className="admin-organizers-table">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Organization</th><th>Email</th><th>City</th><th>Verified</th><th>Action</th></tr>
            </thead>
            <tbody>
              {organizers?.map((o) => (
                <tr key={o.id}>
                  <td>{o.id}</td>
                  <td>{o.organization_name}</td>
                  <td>{o.email || '-'}</td>
                  <td>{o.city || '-'}</td>
                  <td>{o.is_verified ? 'Yes' : 'No'}</td>
                  <td>
                    {!o.is_verified && (
                      <button className="btn btn-primary btn-sm" onClick={() => handleVerify(o.id)}>Verify</button>
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
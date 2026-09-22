import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/OrganizerRegistrations.css';

export default function OrganizerRegistrationsPage() {
  const [registrations, setRegistrations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/registrations');
        setRegistrations(data?.items || []);
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
        <h1 className="dashboard-title">Registrations</h1>

        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Event</th><th>Attendee</th><th>Ticket</th><th>Date</th><th>Status</th></tr></thead>
            <tbody>
              {registrations?.map((r) => (
                <tr key={r.id}>
                  <td>{r.event_title || '-'}</td>
                  <td>{r.user_name || '-'}</td>
                  <td>{r.ticket_type_name || '-'}</td>
                  <td>{r.registration_date?.slice(0, 10)}</td>
                  <td><span className={`status-badge status-${r.status.toLowerCase()}`}>{r.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
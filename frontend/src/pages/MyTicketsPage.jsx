import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './MyTickets.css';
import QRCode from 'qrcode.react';

export default function MyTicketsPage() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!user) return;
      try {
        const data = await apiFetch('/tickets/my');
        setTickets(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">My Tickets</h1>

        {tickets.length === 0 ? (
          <p className="empty-state">You have not registered for an event yet.</p>
        ) : (
          <div className="tickets-grid">
            {tickets.map((t) => (
              <div key={t.id} className={`ticket-card ${t.status.toLowerCase()}`}>
                <div className="ticket-card-header">
                  <h3>{t.event_title}</h3>
                  <span className={`status-badge status-${t.status.toLowerCase()}`}>{t.status}</span>
                </div>
                <div className="ticket-card-body">
                  <p><strong>Type:</strong> {t.ticket_type_name}</p>
                  <p><strong>Date:</strong> {t.event_date || '-'}</p>
                  <p><strong>Location:</strong> {t.event_location || '-'}</p>
                </div>
                {t.status === 'VALID' && (
                  <div className="ticket-card-qr">
                    <QRCode value={t.qr_token || t.ticket_code} size={120} />
                    <p>Scan to check in</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}

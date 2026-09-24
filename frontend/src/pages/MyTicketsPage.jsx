import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import QRCode from 'qrcode.react';
import '../styles/MyTickets.css';

export default function MyTicketsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [checkingId, setCheckingId] = useState(null);

  const reload = async () => {
    const [t, r] = await Promise.all([
      apiFetch('/tickets/my'),
      apiFetch('/registrations/me').catch(() => null),
    ]);
    setTickets(t?.items || []);
    const regs = r?.items || [];
    setPending(regs.filter((x) => x.status === 'PENDING'));
  };

  useEffect(() => {
    async function load() {
      if (!user) return;
      try {
        await reload();
      } catch (e) {
        console.error(e);
        setError(e.message || 'Unable to load tickets.');
        setTickets([]);
        setPending([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  const checkStatus = async (order) => {
    setCheckingId(order.id);
    setError('');
    try {
      const res = await apiFetch('/payments/verify', {
        method: 'POST',
        body: JSON.stringify({ registration_id: order.id }),
      });
      await reload();
      if (!res?.data?.ticket_id) setError('Payment not confirmed yet. If you paid, wait a minute and check again.');
    } catch (e) {
      setError(e.message || 'Verification failed.');
    } finally {
      setCheckingId(null);
    }
  };

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">My Tickets</h1>

        {error && <div className="form-error" role="alert" style={{ marginBottom: 16 }}>{error}</div>}

        {pending.length > 0 && (
          <section className="dashboard-section">
            <h2>Awaiting payment</h2>
            <p className="muted" style={{ marginBottom: 12 }}>
              These orders have no ticket yet. Complete payment to get your QR.
            </p>
            <div className="tickets-grid">
              {pending.map((o) => (
                <div key={o.id} className="ticket-card">
                  <div className="ticket-card-header">
                    <h3>{o.event?.title || 'Event'}</h3>
                    <span className="status-badge status-pending">PENDING</span>
                  </div>
                  <div className="ticket-card-body">
                    <p><strong>Order:</strong> #{o.id}</p>
                    <p><strong>Type:</strong> {o.ticket_type_name}</p>
                  </div>
                  <div className="ticket-card-qr">
                    <button
                      className="btn btn-primary btn-sm"
                      disabled={checkingId === o.id}
                      onClick={() => checkStatus(o)}
                    >
                      {checkingId === o.id ? 'Checking…' : 'Check payment status'}
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => navigate(`/events/${o.event_id}?pay=${o.id}`)}
                    >
                      Complete payment
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {tickets.length === 0 && pending.length === 0 ? (
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
                  <p><strong>Code:</strong> <span className="monospace">{t.ticket_code}</span></p>
                  <p><strong>Date:</strong> {t.event_date || '-'}</p>
                  <p><strong>Location:</strong> {t.event_location || '-'}</p>
                  {t.payment_status && t.payment_status !== 'PAID' && (
                    <p><strong>Payment:</strong> {t.payment_status}</p>
                  )}
                </div>
                {t.status === 'VALID' && (
                  <div className="ticket-card-qr">
                    <QRCode value={t.qr_token || t.ticket_code} size={120} />
                    <p>Scan to check in</p>
                    <Link to={`/user/tickets/${t.id}`} className="btn btn-ghost btn-sm">Details</Link>
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

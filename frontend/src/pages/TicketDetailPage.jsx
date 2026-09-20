import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import QRCode from 'qrcode.react';
import './TicketDetail.css';

export default function TicketDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/tickets/${id}`);
        setTicket(data?.data || data);
      } catch (e) {
        setError(e.message || 'Ticket not found');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <Loading />;
  if (error) return <p className="error">{error}</p>;
  if (!ticket) return <p>Ticket not found.</p>;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <Link to="/user/dashboard" className="back-link">&larr; Back to Dashboard</Link>

        <div className="ticket-detail">
          <div className="ticket-header">
            <h1>{ticket.event_title || 'Event Ticket'}</h1>
            <span className={`ticket-status ${ticket.status.toLowerCase()}`}>
              {ticket.status}
            </span>
          </div>

          <div className="ticket-grid">
            <div className="ticket-info">
              <div className="ticket-field">
                <label>Attendee</label>
                <span>{ticket.attendee_name || user?.first_name || user?.username}</span>
              </div>
              <div className="ticket-field">
                <label>Ticket Type</label>
                <span>{ticket.ticket_type_name || '-'}</span>
              </div>
              <div className="ticket-field">
                <label>Ticket ID</label>
                <span className="monospace">{ticket.ticket_code}</span>
              </div>
              <div className="ticket-field">
                <label>Event Date</label>
                <span>{ticket.event_date || '-'}</span>
              </div>
              <div className="ticket-field">
                <label>Location</label>
                <span>{ticket.event_location || '-'}</span>
              </div>
            </div>

            <div className="ticket-qr-section">
              {ticket.status === 'VALID' && (
                <div className="qr-card">
                  <h3>Scan to Check In</h3>
                  <QRCode value={ticket.qr_token || ticket.ticket_code} size={200} />
                  <p className="qr-note">Show this at the event entrance</p>
                </div>
              )}
              {ticket.status === 'USED' && (
                <div className="ticket-used">
                  <h3>Already Checked In</h3>
                  <p>{ticket.checked_in_at ? new Date(ticket.checked_in_at).toLocaleString() : 'Previously checked in'}</p>
                </div>
              )}
              {['CANCELLED', 'EXPIRED'].includes(ticket.status) && (
                <div className="ticket-invalid">
                  <h3>Ticket {ticket.status}</h3>
                  <p>This ticket cannot be used for entry.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
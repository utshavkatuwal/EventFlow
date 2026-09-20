import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './TicketPage.css';
import QRCode from 'qrcode.react';

export default function TicketPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/tickets/${id}`);
        setTicket(data);
      } catch (e) {
        setError('Ticket not found');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <Loading />;
  if (error) return <p>{error}</p>;
  if (!ticket) return <p>Ticket not found.</p>;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="ticket-container">
          <div className="ticket-card">
            <div className="ticket-header">
              <h1>{ticket.event_title || 'Event Ticket'}</h1>
              <span className={`ticket-status ${ticket.status.toLowerCase()}`}>
                {ticket.status}
              </span>
            </div>

            <div className="ticket-details">
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
                <span>{ticket.ticket_code}</span>
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

            {ticket.status === 'VALID' && (
              <div className="ticket-qr">
                <h3>Scan to Check In</h3>
                <QRCode value={ticket.qr_token || ticket.ticket_code} size={180} />
              </div>
            )}

            {ticket.status === 'USED' && (
              <div className="ticket-checked-in">
                <strong>Checked In</strong>
                <p>{ticket.checked_in_at || '-'}</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}

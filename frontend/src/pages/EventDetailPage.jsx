import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import QRCode from 'qrcode.react';
import './EventDetail.css';

export default function EventDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [ticketTypes, setTicketTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [evData, ttData] = await Promise.all([
          apiFetch(`/events/${id}`).catch(() => null),
          apiFetch(`/events/${id}/tickets`).catch(() => []),
        ]);
        if (evData) {
          setEvent(evData);
          if (ttData && ttData.items) setTicketTypes(ttData.items);
          else if (ttData && Array.isArray(ttData)) setTicketTypes(ttData);
        } else {
          setError('Event not found');
        }
      } catch (e) {
        setError('Failed to load event');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleRegister = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (!selectedTicket) return;
    setRegistering(true);
    try {
      await apiFetch('/registrations', {
        method: 'POST',
        body: JSON.stringify({ event_id: id, ticket_type_id: selectedTicket.id }),
      });
      alert('Registration successful!');
    } catch (e) {
      alert(e.message || 'Registration failed');
    } finally {
      setRegistering(false);
    }
  };

  if (loading) return <Loading />;
  if (error) return <p>{error}</p>;
  if (!event) return <p>Event not found.</p>;

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <Link to="/events" className="event-back">
          &larr; Back to Events
        </Link>

        <div className="event-detail">
          <div className="event-detail-hero">
            {event.cover_image_url ? (
              <img src={event.cover_image_url} alt={event.title} />
            ) : (
              <div className="event-hero-placeholder">{event.title.charAt(0)}</div>
            )}
            <div className="event-detail-header">
              <span className="event-detail-category">{event.category_name || 'Event'}</span>
              <h1>{event.title}</h1>
              <div className="event-detail-meta">
                <span>{formatDate(event.start_date)}</span>
                <span>{event.venue || event.address || event.city || ''}</span>
                <span>{event.organizer_name || 'Unknown'}</span>
              </div>
            </div>
          </div>

          <div className="event-detail-body">
            <div className="event-detail-main">
              <div className="section">
                <h2>About</h2>
                <p>{event.full_description || event.short_description || 'No description available.'}</p>
              </div>
            </div>

            <aside className="event-detail-sidebar">
              <div className="sidebar-card">
                <h3>Tickets</h3>
                {ticketTypes.length > 0 ? (
                  ticketTypes.map((tt) => (
                    <div key={tt.id} className="ticket-option" onClick={() => setSelectedTicket(tt)}>
                      <div className="ticket-info">
                        <span className="ticket-name">{tt.name}</span>
                        <span className="ticket-price">{tt.price > 0 ? `Rs. ${tt.price.toLocaleString()}` : 'Free'}</span>
                      </div>
                      <span className="ticket-avail">
                        {tt.capacity - tt.sold_count} available
                      </span>
                    </div>
                  ))
                ) : (
                  <p>No tickets available.</p>
                )}
                {user && event.status === 'PUBLISHED' && (
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={handleRegister}
                    disabled={registering || !selectedTicket}
                  >
                    {registering ? 'Registering...' : 'Register Now'}
                  </button>
                )}
              </div>

              {user && (
                <div className="sidebar-card">
                  <button className="btn btn-secondary btn-lg" onClick={() => setSaved(!saved)}>
                    {saved ? 'Saved' : 'Save Event'}
                  </button>
                </div>
              )}
            </aside>
          </div>
        </div>
      </main>
    </>
  );
}

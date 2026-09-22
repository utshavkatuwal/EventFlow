import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import '../styles/EventDetail.css';

export default function EventDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [ticketTypes, setTicketTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [evData, ttData] = await Promise.all([
          apiFetch(`/events/${id}`).catch(() => null),
          apiFetch(`/events/${id}/tickets`).catch(() => []),
        ]);
        if (evData) {
          setEvent(evData?.data || evData);
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

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  if (loading) return <Loading />;
  if (error) return <p className="error">{error}</p>;
  if (!event) return <p>Event not found.</p>;

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
              <div className="event-hero-placeholder">{event.title?.charAt(0) || '?'}</div>
            )}
            <div className="event-detail-header">
              <Badge variant="primary">{event.category_name || 'Event'}</Badge>
              <h1>{event.title}</h1>
              <div className="event-detail-meta">
                <span><strong>Date:</strong> {formatDate(event.start_date)}</span>
                <span><strong>Location:</strong> {event.venue || event.address || event.city || '-'}</span>
                <span><strong>Organizer:</strong> {event.organizer_name || 'Unknown'}</span>
              </div>
            </div>
          </div>

          <div className="event-detail-body">
            <div className="event-detail-main">
              <section className="section">
                <h2>About</h2>
                <p>{event.full_description || event.short_description || 'No description available.'}</p>
              </section>

              <section className="section">
                <h2>Details</h2>
                <div className="details-grid">
                  <div className="detail-item">
                    <strong>Date & Time</strong>
                    <span>{formatDate(event.start_date)}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Venue</strong>
                    <span>{event.venue || event.address || event.city || '-'}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Capacity</strong>
                    <span>{event.total_registrations || 0} / {event.max_capacity}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Price</strong>
                    <span>{event.price_min > 0 ? `Rs. ${event.price_min}` : 'Free'}</span>
                  </div>
                </div>
              </section>
            </div>

            <aside className="event-detail-sidebar">
              <div className="sidebar-card">
                <h3>Available Tickets</h3>
                {ticketTypes.length > 0 ? (
                  ticketTypes.map((tt) => (
                    <div
                      key={tt.id}
                      className={`ticket-option ${selectedTicket?.id === tt.id ? 'selected' : ''}`}
                      onClick={() => setSelectedTicket(tt)}
                    >
                      <div className="ticket-info">
                        <span className="ticket-name">{tt.name}</span>
                        <span className="ticket-price">{tt.price > 0 ? `Rs. ${tt.price.toLocaleString()}` : 'Free'}</span>
                      </div>
                      <span className="ticket-avail">
                        {tt.capacity - tt.sold_count} of {tt.capacity} available
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

              <div className="sidebar-card">
                <button
                  className="btn btn-secondary btn-lg"
                  onClick={() => { /* toggle favorite */ }}
                >
                  Save Event
                </button>
              </div>
            </aside>
          </div>
        </div>
      </main>
    </>
  );
}
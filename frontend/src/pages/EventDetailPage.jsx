import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import { getEventImageUrl } from '../utils/images.js';
import Navbar from '../components/Navbar';
import AmbientBackground from '../components/AmbientBackground';
import Footer from '../components/Footer';
import Loading from '../components/Loading';
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
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [evData, ttData] = await Promise.all([apiFetch(`/events/${id}`).catch(() => null), apiFetch(`/events/${id}/tickets`).catch(() => [])]);
        if (evData) {
          setEvent(evData?.data || evData);
          if (ttData?.items) setTicketTypes(ttData.items);
          else if (Array.isArray(ttData)) setTicketTypes(ttData);
        } else setError('Event not found');
      } catch { setError('Failed to load event'); } finally { setLoading(false); }
    }
    load();
  }, [id]);

  const handleRegister = async () => {
    if (!user) { navigate('/login'); return; }
    if (!selectedTicket) return;
    setRegistering(true);
    try {
      await apiFetch('/registrations', { method: 'POST', body: JSON.stringify({ event_id: id, ticket_type_id: selectedTicket.id }) });
      alert('Registration successful!');
    } catch (e) { alert(e.message || 'Registration failed'); } finally { setRegistering(false); }
  };

  const fmtLong = (d) => { if (!d) return '-'; try { return new Date(d).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }); } catch { return '-'; } };

  if (loading) return (<><AmbientBackground /><Navbar /><main className="ed-stage"><Loading /></main></>);
  if (error || !event) return (<><AmbientBackground /><Navbar /><main className="ed-stage"><div className="empty-glass glass-secondary"><h3>{error || 'Event not found'}</h3><Link to="/events" className="btn btn-secondary btn-md" style={{ marginTop: 14 }}>Back to events</Link></div></main></>);

  const hero = getEventImageUrl(event);
  const free = !event.price_min || event.price_min <= 0;

  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="ed-stage">
        <Link to="/events" className="ed-back glass-tert">← All events</Link>
        <div className="ed-hero glass-primary">
          <div className="ed-hero-media"><img src={hero} alt={event.title} onError={(e) => { e.target.onerror = null; e.target.src = getEventImageUrl({ ...event, cover_image_url: null }); }} /><div className="ed-hero-shade" /></div>
          <div className="ed-hero-float">
            <div className="ed-tags">
              <span className="ed-cat glass-tert">{event.category_name || 'Event'}</span>
              {event.status === 'PUBLISHED' && <span className="ed-live"><i />On sale</span>}
            </div>
            <h1>{event.title}</h1>
            <div className="ed-meta-pills">
              <span className="glass-tert">📅 {fmtLong(event.start_date)}</span>
              <span className="glass-tert">📍 {event.venue || event.address || event.city || 'TBA'}</span>
              <span className="glass-tert">👤 {event.organizer_name || 'Organizer'}</span>
            </div>
          </div>
          <button className={`ed-save glass-primary ${saved ? 'on' : ''}`} onClick={() => setSaved(!saved)} aria-pressed={saved} aria-label="Save event">
            <svg width="17" height="17" viewBox="0 0 24 24" fill={saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            {saved ? 'Saved' : 'Save'}
          </button>
        </div>

        <div className="ed-grid">
          <div className="ed-main">
            <section className="ed-card glass-secondary glass-stroke">
              <h2>About this event</h2>
              <p>{event.full_description || event.short_description || 'No description available.'}</p>
            </section>
            <section className="ed-card glass-secondary">
              <h2>Details</h2>
              <div className="ed-details">
                {[
                  ['Date & time', fmtLong(event.start_date)],
                  ['Venue', event.venue || event.address || event.city || '-'],
                  ['City', event.city || '-'],
                  ['Price', free ? 'Free entry' : `Rs. ${Number(event.price_min).toLocaleString()}`],
                ].map(([k, v]) => <div key={k} className="ed-detail"><strong>{k}</strong><span>{v}</span></div>)}
              </div>
            </section>
          </div>
          <aside className="ed-side">
            <div className="ed-tickets glass-primary glass-stroke">
              <h3>Tickets</h3>
              {ticketTypes.length === 0 && <p className="muted">{free ? 'Free entry — just show up (registration may still apply).' : 'Ticket info coming soon.'}</p>}
              {ticketTypes.map((tt) => (
                <div key={tt.id} className={`tk ${selectedTicket?.id === tt.id ? 'sel' : ''}`} onClick={() => setSelectedTicket(tt)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && setSelectedTicket(tt)}>
                  <div className="tk-top"><b>{tt.name}</b><span className="tk-price">{tt.price > 0 ? `Rs. ${Number(tt.price).toLocaleString()}` : 'Free'}</span></div>
                  <small>{Math.max((tt.capacity || 0) - (tt.sold_count || 0), 0)} of {tt.capacity || '—'} left</small>
                </div>
              ))}
              <button className="btn btn-primary btn-lg ed-reg" onClick={handleRegister} disabled={registering || (!selectedTicket && ticketTypes.length > 0)}>
                {registering ? 'Registering…' : user ? 'Register now' : 'Log in to register'}
              </button>
              {!user && <small className="muted center">You'll be asked to log in first.</small>}
            </div>
          </aside>
        </div>
        <Footer />
      </main>
    </>
  );
}

import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import { getEventImageUrl, resolveMediaUrl } from '../utils/images.js';
import { getSavedIds, setSaved } from '../services/saved.js';
import Navbar from '../components/Navbar';
import AmbientBackground from '../components/AmbientBackground';
import Footer from '../components/Footer';
import Loading from '../components/Loading';
import '../styles/EventDetail.css';

export default function EventDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [event, setEvent] = useState(null);
  const [ticketTypes, setTicketTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [registering, setRegistering] = useState(false);
  const [saved, setSaved] = useState(false);
  const [orderMsg, setOrderMsg] = useState('');
  const [pendingOrder, setPendingOrder] = useState(null);
  const [paying, setPaying] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [evData, ttData] = await Promise.all([apiFetch(`/events/${id}`).catch(() => null), apiFetch(`/events/${id}/tickets`).catch(() => [])]);
        if (evData) {
          setEvent(evData?.data || evData);
          const list = ttData?.items || (Array.isArray(ttData) ? ttData : []);
          setTicketTypes(list);
          // Single ticket type: pre-select so Register works on first click.
          if (list.length === 1) setSelectedTicket(list[0]);
        } else setError('Event not found');
      } catch { setError('Failed to load event'); } finally { setLoading(false); }
    }
    load();
  }, [id]);

  // Resume an unpaid order (?pay=<registration_id> from My Tickets).
  useEffect(() => {
    if (!user || !event) return;
    getSavedIds().then((ids) => setSaved(ids.has(event.id))).catch(() => null);
  }, [user, event]);

  const toggleSave = async () => {
    const next = !saved;
    setSaved(next);
    try {
      await setSaved(event.id, next);
    } catch (err) {
      setSaved(!next);
      if (err?.status === 401) navigate('/login');
    }
  };  useEffect(() => {
    const payId = searchParams.get('pay');
    if (!payId || !user) return;
    apiFetch('/registrations/me')
      .then((r) => {
        const order = (r?.items || []).find((x) => String(x.id) === String(payId) && x.status === 'PENDING');
        if (order) {
          setPendingOrder({ registration_id: order.id, amount: null });
          setOrderMsg(`Resuming unpaid order #${order.id} — choose a payment method below.`);
        }
      })
      .catch(() => null);
  }, [searchParams, user]);

  const handleRegister = async () => {
    if (!user) { navigate('/login'); return; }
    if (!selectedTicket) return;
    setRegistering(true);
    setOrderMsg('');
    setPendingOrder(null);
    try {
      const res = await apiFetch('/registrations', { method: 'POST', body: JSON.stringify({ event_id: Number(id), ticket_type_id: selectedTicket.id }) });
      const d = res?.data || {};
      if (d.payment_required) {
        setPendingOrder({ registration_id: d.registration_id, amount: d.amount ?? selectedTicket.price });
        setOrderMsg(`Order #${d.registration_id} created — choose a payment method below to get your QR ticket.`);
      } else {
        setOrderMsg(`Ticket issued! Code: ${d.ticket_code}. Find it under My Tickets.`);
      }
    } catch (e) { setOrderMsg(e.message || 'Registration failed'); } finally { setRegistering(false); }
  };

  const handlePay = async (provider) => {
    if (!pendingOrder) return;
    setPaying(provider);
    setOrderMsg('');
    try {
      const res = await apiFetch('/payments/initiate', {
        method: 'POST',
        body: JSON.stringify({ registration_id: pendingOrder.registration_id, provider }),
      });
      const d = res?.data || {};
      if (d.action_url && d.fields) {
        // eSewa: auto-submit signed form to UAT
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = d.action_url;
        Object.entries(d.fields).forEach(([k, v]) => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = k;
          input.value = v;
          form.appendChild(input);
        });
        document.body.appendChild(form);
        form.submit();
      } else if (d.payment_url) {
        // Khalti: full redirect
        window.location.href = d.payment_url;
      } else {
        setOrderMsg('Payment provider did not return a redirect. Try again.');
      }
    } catch (e) { setOrderMsg(e.message || 'Payment initiation failed'); } finally { setPaying(''); }
  };

  const fmtLong = (d) => { if (!d) return '-'; try { return new Date(d).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }); } catch { return '-'; } };

  if (loading) return (<><AmbientBackground /><Navbar /><main className="ed-stage"><Loading /></main></>);
  if (error || !event) return (<><AmbientBackground /><Navbar /><main className="ed-stage"><div className="empty-glass glass-secondary"><h3>{error || 'Event not found'}</h3><Link to="/events" className="btn btn-secondary btn-md" style={{ marginTop: 14 }}>Back to events</Link></div></main></>);

  const hero = getEventImageUrl(event);
  const free = !event.price_min || event.price_min <= 0;
  const lifecycle = event.lifecycle || 'UPCOMING';
  const cancelled = String(event.status || '').toUpperCase() === 'CANCELLED';
  const ended = lifecycle === 'ENDED' || cancelled;
  const noTickets = !ended && ticketTypes.length === 0;

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
              {event.status === 'PUBLISHED' && lifecycle === 'UPCOMING' && <span className="ed-live"><i />On sale</span>}
              {lifecycle === 'ONGOING' && <span className="ed-live"><i />Happening now</span>}
              {lifecycle === 'ENDED' && <span className="ed-cat glass-tert">Ended</span>}
              {cancelled && <span className="ed-cat glass-tert">Cancelled</span>}
            </div>
            <h1>{event.title}</h1>
            <div className="ed-meta-pills">
              <span className="glass-tert">📅 {fmtLong(event.start_date)}</span>
              <span className="glass-tert">📍 {event.venue || event.address || event.city || 'TBA'}</span>
              <span className="glass-tert">👤 {event.organizer_name || 'Organizer'}</span>
            </div>
          </div>
          <button className={`ed-save glass-primary ${saved ? 'on' : ''}`} onClick={toggleSave} aria-pressed={saved} aria-label="Save event">
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
            {event.video_url && (
              <section className="ed-card glass-secondary">
                <h2>Trailer</h2>
                <video src={resolveMediaUrl(event.video_url)} controls preload="metadata"
                  style={{ width: '100%', borderRadius: 14, maxHeight: 420 }} />
              </section>
            )}
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
              {ended && <p className="muted">{cancelled ? 'This event was cancelled. New purchases are closed.' : 'This event has ended. New purchases are closed.'}</p>}
              {noTickets && <p className="muted">Tickets for this event are not available yet.</p>}
              {ticketTypes.map((tt) => (
                <div key={tt.id} className={`tk ${selectedTicket?.id === tt.id ? 'sel' : ''}`} onClick={() => setSelectedTicket(tt)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && setSelectedTicket(tt)}>
                  <div className="tk-top"><b>{tt.name}</b><span className="tk-price">{tt.price > 0 ? `Rs. ${Number(tt.price).toLocaleString()}` : 'Free'}</span></div>
                  <small>{Math.max((tt.capacity || 0) - (tt.sold_count || 0), 0)} of {tt.capacity || '—'} left</small>
                </div>
              ))}
              <button className="btn btn-primary btn-lg ed-reg" onClick={handleRegister} disabled={registering || ended || noTickets || (!selectedTicket && ticketTypes.length > 0)}>
                {ended ? 'Sales closed' : noTickets ? 'Tickets unavailable' : registering ? 'Registering…' : user ? 'Register now' : 'Log in to register'}
              </button>
              {!ended && !noTickets && !selectedTicket && ticketTypes.length > 1 && (
                <p className="muted center" style={{ marginTop: 8 }}>Select a ticket type above first.</p>
              )}
              {orderMsg && <p className="muted center" style={{ marginTop: 8 }}>{orderMsg}</p>}
              {pendingOrder && !ended && (
                <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
                  <button className="btn btn-primary btn-md" style={{ flex: 1 }} disabled={!!paying} onClick={() => handlePay('ESEWA')}>
                    {paying === 'ESEWA' ? 'Redirecting…' : 'Pay with eSewa'}
                  </button>
                  <button className="btn btn-secondary btn-md" style={{ flex: 1 }} disabled={!!paying} onClick={() => handlePay('KHALTI')}>
                    {paying === 'KHALTI' ? 'Redirecting…' : 'Pay with Khalti'}
                  </button>
                </div>
              )}
              {!user && <small className="muted center">You'll be asked to log in first.</small>}
            </div>
          </aside>
        </div>
        <Footer />
      </main>
    </>
  );
}

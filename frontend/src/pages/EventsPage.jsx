import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import AmbientBackground from '../components/AmbientBackground';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';
import Reveal from '../components/Reveal';
import '../styles/EventsPage.css';

export default function EventsPage() {
  const [searchParams] = useSearchParams();
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || '');
  const [searchQuery, setSearchQuery] = useState('');
  const [city, setCity] = useState('');
  const [price, setPrice] = useState('');
  const [dateFrom, setDateFrom] = useState('');

  useEffect(() => {
    apiFetch('/categories').then((d) => setCategories(d.items || d.data || [])).catch(() => null);
  }, []);

  useEffect(() => {
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        const p = new URLSearchParams({ per_page: 48 });
        if (categoryFilter) p.set('category_id', categoryFilter);
        if (searchQuery.trim()) p.set('q', searchQuery.trim());
        if (city.trim()) p.set('city', city.trim());
        if (price) p.set('price', price);
        if (dateFrom) p.set('date_from', new Date(dateFrom).toISOString());
        const evData = await apiFetch(`/events?${p.toString()}`).catch(() => null);
        if (evData) setEvents(evData.items || evData.data || []);
      } catch (e) { console.error(e); } finally { setLoading(false); }
    }, 300);
    return () => clearTimeout(t);
  }, [categoryFilter, searchQuery, city, price, dateFrom]);

  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="ev-page">
        <Reveal>
          <div className="ev-hero glass-primary glass-stroke">
            <div>
              <p className="kicker">Explore</p>
              <h1>All events</h1>
              <p className="ev-sub">{loading ? 'Loading…' : `${events.length} experience${events.length !== 1 ? 's' : ''} across Nepal`}</p>
            </div>
            <label className="ev-search glass-tert">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
              <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search title, city, vibe…" aria-label="Search events" />
              {searchQuery && <button onClick={() => setSearchQuery('')} aria-label="Clear">×</button>}
            </label>
          </div>
        </Reveal>

        <Reveal delay={80}>
          <div className="ev-filters glass-secondary">
            <button className={`fchip ${!categoryFilter ? 'on' : ''}`} onClick={() => setCategoryFilter('')}>All</button>
            {categories.map((cat) => (
              <button key={cat.id} className={`fchip ${String(categoryFilter) === String(cat.id) ? 'on' : ''}`} onClick={() => setCategoryFilter(String(categoryFilter) === String(cat.id) ? '' : cat.id)}>{cat.name}</button>
            ))}
            <span className="f-count">{events.length} results</span>
          </div>
        </Reveal>

        <Reveal delay={100}>
          <div className="ev-filters glass-secondary" style={{ marginTop: 10 }}>
            <input
              value={city} onChange={(e) => setCity(e.target.value)} placeholder="City"
              aria-label="Filter by city"
              style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 999, padding: '8px 14px', color: '#fff', fontSize: '0.82rem', outline: 'none' }}
            />
            <input
              type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} aria-label="From date"
              style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 999, padding: '8px 14px', color: '#fff', fontSize: '0.82rem', colorScheme: 'dark' }}
            />
            {['', 'free', 'paid'].map((v) => (
              <button key={v || 'any'} className={`fchip ${price === v ? 'on' : ''}`} onClick={() => setPrice(v)}>
                {v || 'Any price'}
              </button>
            ))}
            {(city || price || dateFrom) && (
              <button className="fchip" onClick={() => { setCity(''); setPrice(''); setDateFrom(''); }}>Clear</button>
            )}
          </div>
        </Reveal>

        {loading && <div className="ev-grid">{[0,1,2,3,4,5].map(i => <div key={i} className="skel glass-secondary" />)}</div>}
        {!loading && events.length === 0 && (
          <div className="empty-glass glass-secondary"><h3>Nothing found</h3><p>Try a different search or category.</p></div>
        )}
        {!loading && events.length > 0 && (
          <div className="ev-grid">
            {events.map((ev, i) => (
              <Reveal key={ev.id} delay={Math.min(i * 40, 320)}><EventCard event={ev} /></Reveal>
            ))}
          </div>
        )}
        <Footer />
      </main>
    </>
  );
}

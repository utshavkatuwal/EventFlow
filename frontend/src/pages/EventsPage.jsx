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

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [evData, catData] = await Promise.all([apiFetch('/events?per_page=48').catch(() => null), apiFetch('/categories').catch(() => null)]);
        if (evData) setEvents(evData.items || evData.data || []);
        if (catData) setCategories(catData.items || catData.data || []);
      } catch (e) { console.error(e); } finally { setLoading(false); }
    }
    load();
  }, []);

  const filtered = events.filter((ev) => {
    const mc = !categoryFilter || String(ev.category_id) === String(categoryFilter);
    const q = searchQuery.toLowerCase();
    const ms = !q || ev.title?.toLowerCase().includes(q) || (ev.city || '').toLowerCase().includes(q) || (ev.category_name || '').toLowerCase().includes(q);
    return mc && ms;
  });

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
              <p className="ev-sub">{loading ? 'Loading…' : `${filtered.length} experience${filtered.length !== 1 ? 's' : ''} across Nepal`}</p>
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
            <span className="f-count">{filtered.length} results</span>
          </div>
        </Reveal>

        {loading && <div className="ev-grid">{[0,1,2,3,4,5].map(i => <div key={i} className="skel glass-secondary" />)}</div>}
        {!loading && filtered.length === 0 && (
          <div className="empty-glass glass-secondary"><h3>Nothing found</h3><p>Try a different search or category.</p></div>
        )}
        {!loading && filtered.length > 0 && (
          <div className="ev-grid">
            {filtered.map((ev, i) => (
              <Reveal key={ev.id} delay={Math.min(i * 40, 320)}><EventCard event={ev} /></Reveal>
            ))}
          </div>
        )}
        <Footer />
      </main>
    </>
  );
}

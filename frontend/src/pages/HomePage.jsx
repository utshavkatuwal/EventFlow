import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AmbientBackground from '../components/AmbientBackground';
import Reveal from '../components/Reveal';
import EventCard, { FeaturedCard } from '../components/EventCard';
import { getCategoryPhotos, getEventImageUrl } from '../utils/images.js';
import '../styles/Home.css';

const QUICK_CATS = ['Music', 'Technology', 'Business', 'Arts', 'Sports', 'Community'];

export default function HomePage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [heroQuery, setHeroQuery] = useState('');
  const [heroLoc, setHeroLoc] = useState('');
  const [heroDate, setHeroDate] = useState('');
  const [activeChip, setActiveChip] = useState('All');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [ev, cat] = await Promise.allSettled([apiFetch('/events?per_page=12'), apiFetch('/categories')]);
        if (ev.status === 'fulfilled' && ev.value) {
          const items = ev.value.items || ev.value.data || ev.value || [];
          setEvents(Array.isArray(items) ? items : []);
        }
        if (cat.status === 'fulfilled' && cat.value) {
          const items = cat.value.items || cat.value.data || [];
          setCategories(Array.isArray(items) ? items : []);
        }
      } catch {}
      setLoaded(true);
    }
    load();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    const p = new URLSearchParams();
    if (heroQuery.trim()) p.set('q', heroQuery.trim());
    if (heroLoc.trim()) p.set('city', heroLoc.trim());
    if (heroDate) p.set('date_from', heroDate);
    const qs = p.toString();
    navigate(qs ? `/search?${qs}` : '/events');
  };

  const featured = events[0];
  const trending = events.slice(1, 7);
  const different = events.slice(7, 11);
  const cats = categories.length ? categories : QUICK_CATS.map((n, i) => ({ id: i, name: n }));

  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="ef-home">
        {/* ============ HERO / DISCOVERY ============ */}
        <section className="hero-stage">
          <div className="hero-bg">
            {featured && <img src={getEventImageUrl(featured)} alt="" aria-hidden />}
            <div className="hero-bg-shade" />
          </div>

          <div className="hero-content">
            <Reveal>
              <div className="hero-eyebrow glass-tert"><span className="live-dot" />Live in Nepal · {loaded ? `${events.length}+ events` : 'curated events'} this week</div>
            </Reveal>
            <Reveal delay={70}>
              <h1 className="hero-title">Discover moments<br /><span className="grad">worth remembering.</span></h1>
            </Reveal>
            <Reveal delay={140}>
              <p className="hero-sub">Concerts, tech, culture and community — handpicked across Kathmandu, Pokhara and beyond.</p>
            </Reveal>

            {/* Glass discovery console */}
            <Reveal delay={200}>
              <form className="discovery glass-primary glass-stroke glass-sheen" onSubmit={handleSearch}>
                <div className="disc-row">
                  <label className="disc-field">
                    <span className="disc-label">Search</span>
                    <span className="disc-input">
                      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
                      <input value={heroQuery} onChange={(e) => setHeroQuery(e.target.value)} placeholder="Artist, event, vibe…" aria-label="Search events" />
                    </span>
                  </label>
                  <span className="disc-div" />
                  <label className="disc-field">
                    <span className="disc-label">Location</span>
                    <span className="disc-input">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                      <input value={heroLoc} onChange={(e) => setHeroLoc(e.target.value)} placeholder="Kathmandu" aria-label="Location" />
                    </span>
                  </label>
                  <span className="disc-div" />
                  <label className="disc-field">
                    <span className="disc-label">Date</span>
                    <span className="disc-input"><input type="date" value={heroDate} onChange={(e) => setHeroDate(e.target.value)} aria-label="Date" /></span>
                  </label>
                  <button type="submit" className="btn btn-primary disc-go">Explore</button>
                </div>
                <div className="disc-chips">
                  {['All', ...QUICK_CATS.slice(0, 5)].map((c) => (
                    <button key={c} type="button" className={`dchip ${activeChip === c ? 'on' : ''}`} onClick={() => { setActiveChip(c); if (c !== 'All') navigate(`/search?q=${encodeURIComponent(c)}`); }}>{c}</button>
                  ))}
                  <Link to="/events" className="dchip ghost">Browse all →</Link>
                </div>
              </form>
            </Reveal>

            {/* Floating mini previews */}
            {featured && (
              <div className="hero-floats">
                <Reveal delay={300} className="float-a">
                  <Link to={`/events/${featured.id}`} className="mini-preview glass-primary">
                    <img src={getEventImageUrl(featured)} alt="" loading="lazy" />
                    <span><b>{featured.title?.slice(0, 28)}{(featured.title?.length || 0) > 28 ? '…' : ''}</b><small>{featured.city || 'Kathmandu'} · Popular near you</small></span>
                    <span className="mini-go">→</span>
                  </Link>
                </Reveal>
                <div className="float-b glass-tert">
                  <span className="avatars"><i /><i /><i /><i /></span>
                  <span><b>2.4k</b> going this weekend</span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ============ TRENDING ============ */}
        <section className="ef-section">
          <Reveal>
            <div className="sec-head">
              <div><p className="kicker">Trending near you</p><h2>Tonight & this weekend</h2></div>
              <Link to="/events" className="sec-more glass-tert">View all <span>→</span></Link>
            </div>
          </Reveal>
          <div className="rail">
            {!loaded && [0,1,2].map(i => <div key={i} className="skel glass-secondary" />)}
            {loaded && trending.length === 0 && <div className="empty-glass glass-secondary"><h3>No events yet</h3><p>Publish an event to see it trending here.</p></div>}
            {trending.map((ev, i) => (
              <Reveal key={ev.id} delay={i * 60} className="rail-item"><EventCard event={ev} /></Reveal>
            ))}
          </div>
        </section>

        {/* ============ EXPLORE BY EXPERIENCE ============ */}
        <section className="ef-section">
          <Reveal>
            <div className="sec-head">
              <div><p className="kicker">Explore by experience</p><h2>What are you in the mood for?</h2></div>
            </div>
          </Reveal>
          <div className="xp-grid">
            {cats.slice(0, 6).map((c, i) => {
              const photos = getCategoryPhotos(c.name);
              const tall = i === 0 || i === 3;
              return (
                <Reveal key={c.id ?? c.name} delay={i * 50} className={tall ? 'xp-tall' : ''}>
                  <Link to={c.id ? `/categories/${c.id}` : `/search?q=${encodeURIComponent(c.name)}`} className={`xp-tile glass-sheen ${tall ? 'tall' : ''}`}>
                    <img src={photos[i % photos.length]} alt={c.name} loading="lazy" onError={(e) => { e.target.onerror = null; e.target.src = 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&q=80&auto=format&fit=crop'; }} />
                    <span className="xp-shade" />
                    <span className="xp-count glass-tert">{3 + ((i * 7) % 9)} events</span>
                    <span className="xp-label"><b>{c.name}</b><small>Explore →</small></span>
                  </Link>
                </Reveal>
              );
            })}
          </div>
        </section>

        {/* ============ FEATURED THIS WEEK — asymmetric ============ */}
        {featured && (
          <section className="ef-section feat-grid">
            <Reveal>
              <p className="kicker">Featured this week</p>
              <h2 className="feat-h">One night you shouldn't miss</h2>
            </Reveal>
            <div className="feat-layout">
              <Reveal className="feat-main"><FeaturedCard event={featured} /></Reveal>
              <div className="feat-side">
                {events.slice(1, 3).map((ev, i) => (
                  <Reveal key={ev.id} delay={i * 80}><EventCard event={ev} variant="horizontal" /></Reveal>
                ))}
                <Reveal delay={160}>
                  <Link to="/events" className="feat-more glass-secondary glass-sheen">
                    <span><b>{Math.max(events.length - 3, 12)}+ more events</b><small>Across Nepal this month</small></span>
                    <span className="feat-more-arrow">→</span>
                  </Link>
                </Reveal>
              </div>
            </div>
          </section>
        )}

        {/* ============ SOMETHING DIFFERENT — editorial ============ */}
        {different.length > 0 && (
          <section className="ef-section">
            <Reveal>
              <div className="sec-head">
                <div><p className="kicker">Discover something different</p><h2>Off the beaten path</h2></div>
                <Link to="/events" className="sec-more glass-tert">Surprise me <span>→</span></Link>
              </div>
            </Reveal>
            <div className="editorial">
              <div className="ed-col">
                {different.slice(0, 2).map(ev => <EventCard key={ev.id} event={ev} variant="horizontal" />)}
              </div>
              <div className="ed-col ed-offset">
                {different.slice(2, 4).map(ev => <EventCard key={ev.id} event={ev} variant="compact" />)}
                <Link to="/search" className="ed-quote glass-primary glass-stroke">
                  <b>“The best weekend plans start here.”</b>
                  <small>Advanced search with dates, city & category →</small>
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* ============ JOURNEY ============ */}
        <section className="ef-section">
          <Reveal>
            <div className="journey glass-primary glass-stroke">
              <div className="j-head"><p className="kicker">Your event journey</p><h2>From discovery to dance floor</h2></div>
              <div className="j-steps">
                {[
                  { n: '01', t: 'Discover', d: 'Curated picks, real photos, honest pricing. Filter by vibe, date and city.' },
                  { n: '02', t: 'Book in seconds', d: 'Pick a ticket, check out instantly, get your QR — no printing, no queues.' },
                  { n: '03', t: 'Show up & shine', d: 'Contactless check-in at the door. Save favourites and relive past nights.' },
                ].map((s, i) => (
                  <div key={s.n} className="j-step">
                    <span className="j-num">{s.n}</span>
                    <h3>{s.t}</h3><p>{s.d}</p>
                    {i < 2 && <span className="j-line" />}
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        </section>

        {/* ============ CTA ============ */}
        <section className="ef-section">
          <Reveal>
            <div className="cta glass-primary glass-stroke glass-sheen">
              <img className="cta-img" src="https://images.unsplash.com/photo-1511578314322-379afb476865?w=1600&q=80&auto=format&fit=crop" alt="" loading="lazy" />
              <div className="cta-shade" />
              <div className="cta-inner">
                <p className="kicker light">For organizers</p>
                <h2>Host something unforgettable.</h2>
                <p>Create an event, sell tickets, scan QR check-ins and track everything live.</p>
                <div className="cta-btns">
                  <Link to="/register" className="btn btn-primary btn-lg">Create an event</Link>
                  <Link to="/events" className="btn btn-secondary btn-lg">Browse events</Link>
                </div>
              </div>
            </div>
          </Reveal>
        </section>

        <Footer />
      </main>
    </>
  );
}

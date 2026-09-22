import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';
import '../styles/Home.css';

export default function HomePage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState(null);
  const [categories, setCategories] = useState(null);
  const [heroQuery, setHeroQuery] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [ev, cat] = await Promise.allSettled([
          apiFetch('/events?per_page=6'),
          apiFetch('/categories'),
        ]);
        if (ev.status === 'fulfilled' && ev.value) setEvents(ev.value);
        if (cat.status === 'fulfilled' && cat.value) setCategories(cat.value);
      } catch {}
      setLoaded(true);
    }
    load();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(heroQuery.trim() ? `/search?q=${encodeURIComponent(heroQuery.trim())}` : '/events');
  };

  return (
    <>
      <Navbar />
      <main>
        <section className="hero">
          <div className="hero-bg-orb" />
          <div className="hero-bg-orb orb-2" />
          <div className="hero-inner">
            <p className="hero-eyebrow">Event Discovery Platform</p>
            <h1 className="hero-title">Discover Events<br />in Nepal</h1>
            <p className="hero-desc">Find and register for technology, business, arts, and community events happening across Nepal.</p>
            <form className="hero-form" onSubmit={handleSearch}>
              <div className="hero-input-wrap">
                <svg className="hero-input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" placeholder="Search by title, location, or category..." value={heroQuery} onChange={(e) => setHeroQuery(e.target.value)} />
              </div>
              <button type="submit" className="btn btn-primary btn-lg">Search</button>
            </form>
            <div className="hero-chips">
              <Link to="/events" className="chip">Browse All Events</Link>
              <Link to="/register" className="chip">Host an Event</Link>
              <Link to="/search" className="chip">Advanced Search</Link>
            </div>
          </div>
        </section>

        {categories?.items?.length > 0 && (
          <section className="section">
            <div className="section-head">
              <h2>Categories</h2>
              <Link to="/events" className="section-more">View All →</Link>
            </div>
            <div className="cat-grid">
              {categories.items.map((c) => (
                <Link key={c.id} to={`/categories/${c.id}`} className="cat-card">
                  <span className="cat-name">{c.name}</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="section">
          <div className="section-head">
            <h2>Featured Events</h2>
            <Link to="/events" className="section-more">View All →</Link>
          </div>
          {!loaded && (
            <div className="empty-box">
              <div className="empty-spinner" />
              <p>Loading events...</p>
            </div>
          )}
          {loaded && events?.items?.length === 0 && (
            <div className="empty-box">
              <h3>No events yet</h3>
              <p>Events will appear here once organizers publish them.</p>
              <Link to="/register" className="btn btn-primary btn-md" style={{ marginTop: 16 }}>Become an Organizer</Link>
            </div>
          )}
          {loaded && events?.items?.length > 0 && (
            <div className="events-grid">
              {events.items.map((ev) => <EventCard key={ev.id} event={ev} />)}
            </div>
          )}
          {loaded && !events && (
            <div className="empty-box">
              <h3>Backend not connected</h3>
              <p>Start the backend server to see live events, categories, and stats.</p>
            </div>
          )}
        </section>

        <section className="section">
          <div className="section-head"><h2>How It Works</h2></div>
          <div className="steps-row">
            <div className="step-card">
              <span className="step-num">01</span>
              <h3>Discover</h3>
              <p>Browse curated events across Nepal. Filter by category, date, location, and price.</p>
            </div>
            <div className="step-card">
              <span className="step-num">02</span>
              <h3>Register</h3>
              <p>Select your ticket, complete registration, and receive your digital ticket instantly.</p>
            </div>
            <div className="step-card">
              <span className="step-num">03</span>
              <h3>Attend</h3>
              <p>Show your QR ticket at the entrance. Fast, secure, contactless check-in.</p>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="cta-box">
            <h2>Organizing an Event?</h2>
            <p>Create your event, manage tickets, track registrations, and check in attendees.</p>
            <div className="cta-btns">
              <Link to="/register" className="btn btn-primary btn-lg">Get Started Free</Link>
              <Link to="/events" className="btn btn-ghost btn-lg">Browse Events</Link>
            </div>
          </div>
        </section>

        <Footer />
      </main>
    </>
  );
}

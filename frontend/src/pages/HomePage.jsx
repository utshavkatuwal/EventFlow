import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import EventCard from '../components/EventCard';
import Loading from '../components/Loading';
import './Home.css';

export default function HomePage() {
  const [events, setEvents] = useState(null);
  const [categories, setCategories] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [evData, catData, statsData] = await Promise.all([
          apiFetch('/events?per_page=6').catch(() => null),
          apiFetch('/categories').catch(() => null),
          apiFetch('/events/stats').catch(() => null),
        ]);
        if (evData) setEvents(evData);
        if (catData) setCategories(catData);
        if (statsData) setStats(statsData);
      } catch (e) {
        setError('Failed to load events. Please try again.');
      }
    }
    load();
  }, []);

  return (
    <>
      <Navbar />
      <main className="main-content">
        <section className="hero">
          <h1>Discover Events in Nepal</h1>
          <p className="hero-subtitle">
            Find and register for technology, business, arts, and community events across Nepal.
          </p>
          <div className="hero-search">
            <input type="text" placeholder="Search events by title, location, or category..." />
            <Link to="/events" className="btn btn-primary">
              Search
            </Link>
          </div>
        </section>

        {stats && (
          <section className="home-stats">
            <div className="stat">
              <span className="stat-number">{stats.total_events}</span>
              <span className="stat-label">Events</span>
            </div>
            <div className="stat">
              <span className="stat-number">{stats.upcoming_events}</span>
              <span className="stat-label">Upcoming</span>
            </div>
            <div className="stat">
              <span className="stat-number">{stats.total_registrations}</span>
              <span className="stat-label">Registrations</span>
            </div>
          </section>
        )}

        {categories && categories.items && categories.items.length > 0 && (
          <section className="home-categories">
            <h2>Browse by Category</h2>
            <div className="category-grid">
              {categories.items.map((cat) => (
                <Link key={cat.id} to={`/events?category=${cat.id}`} className="category-link">
                  {cat.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="home-events">
          <h2>Featured Events</h2>
          {error && <p>{error}</p>}
          {!events && !error && <Loading />}
          {events && events.items && events.items.length === 0 && (
            <p>No events available yet. Check back soon!</p>
          )}
          {events && events.items && events.items.length > 0 && (
            <div className="events-grid">
              {events.items.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </section>

        <section className="home-cta">
          <h2>Organizing an Event?</h2>
          <p>Create your first event and start reaching attendees in Nepal.</p>
          <Link to="/register" className="btn btn-primary">
            Get Started
          </Link>
        </section>
      </main>
    </>
  );
}

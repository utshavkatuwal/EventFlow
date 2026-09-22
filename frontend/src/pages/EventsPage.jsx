import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import EventCard from '../components/EventCard';
import Loading from '../components/Loading';
import '../styles/EventsPage.css';

export default function EventsPage() {
  const [searchParams] = useSearchParams();
  const [events, setEvents] = useState(null);
  const [categories, setCategories] = useState(null);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || '');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [evData, catData] = await Promise.all([
          apiFetch('/events').catch(() => null),
          apiFetch('/categories').catch(() => null),
        ]);
        setEvents(evData);
        setCategories(catData);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredEvents = events?.items?.filter((ev) => {
    const matchCategory = !categoryFilter || ev.category_id == categoryFilter;
    const matchSearch = !searchQuery || ev.title.toLowerCase().includes(searchQuery.toLowerCase()) || (ev.city || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchCategory && matchSearch;
  });

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="events-header">
          <h1>All Events</h1>
          <div className="events-search">
            <input
              type="text"
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {categories && categories.items && (
          <div className="events-filters">
            <button
              className={`filter-chip ${!categoryFilter ? 'active' : ''}`}
              onClick={() => setCategoryFilter('')}
            >
              All
            </button>
            {categories.items.map((cat) => (
              <button
                key={cat.id}
                className={`filter-chip ${categoryFilter == cat.id ? 'active' : ''}`}
                onClick={() => setCategoryFilter(cat.id)}
              >
                {cat.name}
              </button>
            ))}
          </div>
        )}

        {loading && <Loading />}
        {!loading && (!filteredEvents || filteredEvents.length === 0) && (
          <p>No events found matching your criteria.</p>
        )}
        {!loading && filteredEvents && filteredEvents.length > 0 && (
          <div className="events-grid">
            {filteredEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </main>
    </>
  );
}

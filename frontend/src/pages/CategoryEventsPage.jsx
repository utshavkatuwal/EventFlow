import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './CategoryEvents.css';
import SimpleEventCard from '../components/SimpleEventCard';

export default function CategoryEventsPage({ match }) {
  const categoryId = match.params.id;
  const [category, setCategory] = useState(null);
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [catData, evData] = await Promise.all([
          apiFetch(`/categories/${categoryId}`),
          apiFetch(`/events?category_id=${categoryId}`),
        ]);
        setCategory(catData?.data || catData);
        setEvents(evData?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [categoryId]);

  if (loading) return <Loading />;
  if (!category) return <p>Category not found.</p>;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="category-header">
          <h1>{category.name}</h1>
          {category.description && <p>{category.description}</p>}
        </div>

        {events && events.length === 0 ? (
          <p className="empty-state">No events in this category yet.</p>
        ) : (
          <div className="events-grid">
            {events?.map((ev) => (
              <SimpleEventCard key={ev.id} event={ev} />
            ))}
          </div>
        )}
      </main>
    </>
  );
}
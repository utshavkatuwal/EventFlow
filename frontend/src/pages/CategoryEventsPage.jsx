import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import SimpleEventCard from '../components/SimpleEventCard';
import '../styles/CategoryEvents.css';

export default function CategoryEventsPage() {
  const { id } = useParams();
  const [category, setCategory] = useState(null);
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [catData, evData] = await Promise.all([
          apiFetch(`/categories/${id}`),
          apiFetch(`/events?category_id=${id}`),
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
  }, [id]);

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

import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './OrganizerMyEvents.css';
import SimpleEventCard from '../components/SimpleEventCard';

export default function OrganizerMyEventsPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/events');
        setEvents(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="organizer-events-header">
          <h1>My Events</h1>
        </div>

        {events && events.length === 0 ? (
          <p className="empty-state">Create your first event to start managing registrations.</p>
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
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './PastEvents.css';
import SimpleEventCard from '../components/SimpleEventCard';

export default function PastEventsPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!user) return;
      try {
        const data = await apiFetch('/user/past');
        setEvents(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Past Events</h1>

        {events && events.length === 0 ? (
          <p className="empty-state">No past events.</p>
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

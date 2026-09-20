import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import RequireAuth from '../components/RequireAuth';
import ProtectedRoute from '../components/ProtectedRoute';
import Loading from '../components/Loading';
import { EventCard } from '../components/EventCard';

export default function UserDashboard({ events }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;

  const upcoming = events?.filter((ev) => new Date(ev.start_date) >= new Date());
  const past = events?.filter((ev) => new Date(ev.start_date) < new Date());
  const saved = events;

  return (
    <>
      <h1>My Dashboard</h1>

      <section>
        <h2>My Tickets</h2>
        <p>Your tickets will appear here.</p>
      </section>

      <section>
        <h2>Upcoming Events</h2>
        {upcoming?.length > 0 ? (
          <div className="events-grid">
            {upcoming.map((ev) => <EventCard key={ev.id} event={ev} />)}
          </div>
        ) : <p>No upcoming events.</p>}
      </section>

      <section>
        <h2>Past Events</h2>
        {past?.length > 0 ? (
          <div className="events-grid">
            {past.map((ev) => <EventCard key={ev.id} event={ev} />)}
          </div>
        ) : <p>No past events.</p>}
      </section>

      <section>
        <h2>Saved Events</h2>
        <p>Your saved events will appear here.</p>
      </section>
    </>
  );
}

export function OrganizerDashboard({ events }) {
  return (
    <>
      <h1>Organizer Dashboard</h1>
      <p>Manage your events and view registrations.</p>
      {events?.length > 0 && (
        <div className="events-grid">
          {events.map((ev) => <EventCard key={ev.id} event={ev} />)}
        </div>
      )}
    </>
  );
}

export function AdminDashboard({ events }) {
  return (
    <>
      <h1>Admin Dashboard</h1>
      <p>Platform overview and moderation tools.</p>
      {events?.length > 0 && (
        <div className="events-grid">
          {events.map((ev) => <EventCard key={ev.id} event={ev} />)}
        </div>
      )}
    </>
  );
}

import React from 'react';
import '../styles/Card.css';
import { Link } from 'react-router-dom';

export default function SimpleEventCard({ event }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <article className="event-card">
      <div className="event-card-image">
        {event.cover_image_url ? (
          <img src={event.cover_image_url} alt={event.title} loading="lazy" />
        ) : (
          <div className="event-card-placeholder">{event.title?.charAt(0) || '?'}</div>
        )}
      </div>
      <div className="event-card-body">
        <span className="event-card-category">{event.category_name || 'Event'}</span>
        <h3 className="event-card-title">
          <Link to={`/events/${event.id}`}>{event.title}</Link>
        </h3>
        <div className="event-card-meta">
          <span>{formatDate(event.start_date)}</span>
          <span>{event.city || ''}</span>
        </div>
      </div>
    </article>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import Badge from './Badge';
import '../styles/EventList.css';

export default function EventList({ events, title = '' }) {
  if (!events || events.length === 0) {
    return <p className="empty-state">No events found.</p>;
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <section className="event-list">
      {title && <h2 className="event-list-title">{title}</h2>}
      <div className="event-grid">
        {events.map((ev) => (
          <article key={ev.id} className="event-card">
            <div className="event-card-image">
              {ev.cover_image_url ? (
                <img src={ev.cover_image_url} alt={ev.title} loading="lazy" />
              ) : (
                <div className="event-card-placeholder">{ev.title?.charAt(0) || '?'}</div>
              )}
            </div>
            <div className="event-card-body">
              <Badge variant="primary" size="sm">{ev.category_name || 'Event'}</Badge>
              <h3 className="event-card-title">
                <Link to={`/events/${ev.id}`}>{ev.title}</Link>
              </h3>
              <div className="event-card-meta">
                <span>{formatDate(ev.start_date)}</span>
                <span>{ev.city || ''}</span>
              </div>
              <div className="event-card-footer">
                <span className="event-card-price">
                  {ev.price_min > 0 ? `Rs. ${ev.price_min}` : 'Free'}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
import React from 'react';
import './Card.css';

export default function EventCard({ event, onSave, saved }) {
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
          <div className="event-card-placeholder" aria-hidden="true">
            {event.title?.charAt(0) || '?'}
          </div>
        )}
      </div>
      <div className="event-card-body">
        <span className="event-card-category">{event.category_name || 'Event'}</span>
        <h3 className="event-card-title">
          <a href={`/events/${event.id}`}>{event.title}</a>
        </h3>
        <div className="event-card-meta">
          <span>{formatDate(event.start_date)}</span>
          <span>{event.city || ''}</span>
        </div>
        <div className="event-card-footer">
          <span className="event-card-price">
            {event.price_min > 0 ? `Rs. ${event.price_min}` : 'Free'}
          </span>
          {onSave && (
            <button
              className={`btn-save ${saved ? 'saved' : ''}`}
              onClick={() => onSave(event.id)}
              aria-label={saved ? 'Remove from saved' : 'Save event'}
            >
              {saved ? 'Saved' : 'Save'}
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

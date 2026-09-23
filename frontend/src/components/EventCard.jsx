import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { getEventImageUrl } from '../utils/images.js';
import '../styles/Card.css';

function fmtDate(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch { return ''; }
}
function fmtDay(dateStr) {
  if (!dateStr) return '--';
  try { return new Date(dateStr).getDate().toString().padStart(2, '0'); } catch { return '--'; }
}
function fmtMon(dateStr) {
  if (!dateStr) return '';
  try { return new Date(dateStr).toLocaleDateString('en-US', { month: 'short' }).toUpperCase(); } catch { return ''; }
}

export function PriceTag({ event }) {
  const free = !event?.price_min || event.price_min <= 0;
  return <span className={`price-pill ${free ? 'free' : ''}`}>{free ? 'Free' : `Rs. ${Number(event.price_min).toLocaleString()}`}</span>;
}

/* FEATURED — cinematic image + floating glass panel */
export function FeaturedCard({ event }) {
  const img = getEventImageUrl(event);
  return (
    <Link to={`/events/${event.id}`} className="ef-featured glass-sheen group" aria-label={event.title}>
      <div className="ef-featured-media">
        <img src={img} alt={event.title} loading="lazy" onError={(e) => { e.target.onerror = null; e.target.src = getEventImageUrl({ ...event, cover_image_url: null }); }} />
        <div className="ef-featured-shade" />
      </div>
      <div className="ef-featured-top">
        <span className="ef-badge glass-tert"><span className="dot" />Featured this week</span>
        <PriceTag event={event} />
      </div>
      <div className="ef-featured-panel glass-secondary glass-stroke">
        <div className="ef-dateblock"><span className="d">{fmtDay(event.start_date)}</span><span className="m">{fmtMon(event.start_date)}</span></div>
        <div className="ef-finfo">
          <span className="ef-cat">{event.category_name || 'Event'} · {event.city || 'Nepal'}</span>
          <h3>{event.title}</h3>
          <span className="ef-cta">View details <span aria-hidden>→</span></span>
        </div>
      </div>
    </Link>
  );
}

/* STANDARD — image + floating glass info that rises on hover */
export default function EventCard({ event, onSave, saved, variant = 'standard' }) {
  const [liked, setLiked] = useState(!!saved);
  const img = getEventImageUrl(event);

  const toggleSave = (e) => {
    e.preventDefault(); e.stopPropagation();
    const next = !liked; setLiked(next);
    onSave?.(event.id, next);
  };

  if (variant === 'featured') return <FeaturedCard event={event} />;

  if (variant === 'horizontal') {
    return (
      <Link to={`/events/${event.id}`} className="ef-h glass-secondary glass-sheen">
        <div className="ef-h-media"><img src={img} alt={event.title} loading="lazy" onError={(e) => { e.target.onerror = null; e.target.src = getEventImageUrl({ ...event, cover_image_url: null }); }} /></div>
        <div className="ef-h-body">
          <span className="ef-cat">{event.category_name || 'Event'}</span>
          <h3>{event.title}</h3>
          <div className="ef-h-meta"><span>{fmtDate(event.start_date)}</span><i>·</i><span>{event.city || 'Nepal'}</span></div>
        </div>
        <div className="ef-h-side"><PriceTag event={event} /><span className="ef-arrow">→</span></div>
      </Link>
    );
  }

  if (variant === 'compact') {
    return (
      <Link to={`/events/${event.id}`} className="ef-compact glass-tert glass-sheen">
        <div className="ef-c-media"><img src={img} alt={event.title} loading="lazy" onError={(e) => { e.target.onerror = null; e.target.src = getEventImageUrl({ ...event, cover_image_url: null }); }} /></div>
        <div className="ef-c-body">
          <span className="ef-cat">{event.category_name || 'Event'}</span>
          <h4>{event.title}</h4>
          <span className="ef-c-meta">{fmtDate(event.start_date)} · {event.city || 'Nepal'}</span>
        </div>
      </Link>
    );
  }

  return (
    <article className="ef-card glass-secondary glass-sheen">
      <Link to={`/events/${event.id}`} className="ef-media" aria-label={event.title}>
        <img src={img} alt={event.title || 'Event'} loading="lazy" onError={(e) => { e.target.onerror = null; e.target.src = getEventImageUrl({ ...event, cover_image_url: null }); }} />
        <div className="ef-media-shade" />
        <div className="ef-media-top">
          <span className="ef-datepill glass-primary"><b>{fmtDay(event.start_date)}</b><span>{fmtMon(event.start_date)}</span></span>
          <button className={`ef-save glass-primary ${liked ? 'on' : ''}`} onClick={toggleSave} aria-label={liked ? 'Remove from saved' : 'Save event'} aria-pressed={liked}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </button>
        </div>
        <div className="ef-glassbar glass-primary">
          <div className="ef-glassbar-left"><span className="ef-cat">{event.category_name || 'Event'}</span><span className="ef-loc">{event.city || 'Nepal'}</span></div>
          <PriceTag event={event} />
        </div>
      </Link>
      <div className="ef-body">
        <h3 className="ef-title"><Link to={`/events/${event.id}`}>{event.title}</Link></h3>
        <div className="ef-meta"><span>{fmtDate(event.start_date)}</span><i>·</i><span>{event.venue || event.city || 'TBA'}</span></div>
      </div>
    </article>
  );
}

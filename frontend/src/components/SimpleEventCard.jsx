import React from 'react';
import EventCard from './EventCard';

export default function SimpleEventCard({ event, variant = 'compact' }) {
  return <EventCard event={event} variant={variant} />;
}

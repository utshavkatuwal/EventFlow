import React from 'react';
import './NotificationBadge.css';

export default function NotificationBadge({ count }) {
  if (!count || count === 0) return null;
  return (
    <span className="notification-badge">
      <span className="badge">{count > 9 ? '9+' : count}</span>
    </span>
  );
}

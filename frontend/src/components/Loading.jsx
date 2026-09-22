import React from 'react';
import '../styles/Loading.css';

export default function Loading({ text = 'Loading...' }) {
  return (
    <div className="loading" role="status" aria-live="polite">
      <div className="loading-spinner" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}

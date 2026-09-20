import React from 'react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">EventFlow</div>
        <p className="footer-tagline">Discover events in Nepal.</p>
        <div className="footer-links">
          <a href="/events">Events</a>
        </div>
        <p className="footer-copy">EventFlow. All rights reserved.</p>
      </div>
    </footer>
  );
}

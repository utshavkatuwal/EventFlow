import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import AmbientBackground from './AmbientBackground';
import '../styles/Layout.css';

function MobileTabbar() {
  const loc = useLocation();
  const tabs = [
    { path: '/', label: 'Home', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9 21v-6h6v6"/></svg> },
    { path: '/events', label: 'Explore', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg> },
    { path: '/search', label: 'Search', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 1-.1 1.2l2 1.6-2 3.4-2.4-1a7 7 0 0 1-2 1.2L14 20h-4l-.5-2.6a7 7 0 0 1-2-1.2l-2.4 1-2-3.4 2-1.6A7 7 0 0 1 5 12a7 7 0 0 1 .1-1.2l-2-1.6 2-3.4 2.4 1a7 7 0 0 1 2-1.2L10 3h4l.5 2.6a7 7 0 0 1 2 1.2l2.4-1 2 3.4-2 1.6c.06.4.1.8.1 1.2Z"/></svg> },
    { path: '/user/dashboard', label: 'Tickets', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2.5 2.5 0 0 0 0 5v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2.5 2.5 0 0 0 0-5Z"/><path d="M13 5v2m0 4v2m0 4v2"/></svg> },
  ];
  const isActive = (p) => p === '/' ? loc.pathname === '/' : loc.pathname.startsWith(p);
  return (
    <nav className="mobile-tabbar" aria-label="Mobile">
      <div className="mobile-tabbar-inner">
        {tabs.map(t => (
          <Link key={t.path} to={t.path} className={`mobile-tab ${isActive(t.path) ? 'active' : ''}`}>
            {t.icon}<span>{t.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}

export default function Layout({ children }) {
  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="main-content">{children}</main>
      <MobileTabbar />
    </>
  );
}

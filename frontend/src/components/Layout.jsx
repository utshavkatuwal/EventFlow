import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import AmbientBackground from './AmbientBackground';
import { useAuth } from '../context/AuthContext';
import { getRole } from '../utils/roles';
import '../styles/Layout.css';

const ICONS = {
  home: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9 21v-6h6v6"/></svg>,
  explore: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>,
  search: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>,
  ticket: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2.5 2.5 0 0 0 0 5v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2.5 2.5 0 0 0 0-5Z"/><path d="M13 5v2m0 4v2m0 4v2"/></svg>,
  dash: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>,
  plus: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>,
  scan: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/></svg>,
  wallet: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M20 7H5a2 2 0 0 1 0-4h14v4"/><path d="M20 7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5"/><circle cx="17" cy="14" r="1.2"/></svg>,
};

function tabsFor(role) {
  if (role === 'admin') {
    return [
      { path: '/admin/dashboard', label: 'Admin', icon: ICONS.dash },
      { path: '/admin/organizers', label: 'Orgs', icon: ICONS.ticket },
      { path: '/admin/withdrawals', label: 'Payouts', icon: ICONS.wallet },
      { path: '/admin/events', label: 'Events', icon: ICONS.explore },
    ];
  }
  if (role === 'organizer') {
    return [
      { path: '/organizer/dashboard', label: 'Home', icon: ICONS.dash },
      { path: '/organizer/my-events', label: 'Events', icon: ICONS.ticket },
      { path: '/organizer/create-event', label: 'Create', icon: ICONS.plus },
      { path: '/organizer/checkin', label: 'Scan', icon: ICONS.scan },
    ];
  }
  return [
    { path: '/', label: 'Home', icon: ICONS.home },
    { path: '/events', label: 'Explore', icon: ICONS.explore },
    { path: '/search', label: 'Search', icon: ICONS.search },
    { path: '/user/tickets', label: 'Tickets', icon: ICONS.ticket },
  ];
}

export function MobileTabbar() {
  const loc = useLocation();
  const { user } = useAuth();
  const tabs = tabsFor(getRole(user));
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

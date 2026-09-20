import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import './Navbar.css';

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const [user, setUser] = useState(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('user');
      if (stored) setUser(JSON.parse(stored));
    } catch { }
  }, [location.pathname]);

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/events', label: 'Events' },
  ];

  if (user) {
    const dashboardPath = user.role === 'organizer' || user.role === 'admin'
      ? '/organizer/dashboard'
      : '/user/dashboard';
    navLinks.push({ path: dashboardPath, label: 'Dashboard' });
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          EventFlow
        </Link>

        <nav className={`navbar-nav ${mobileOpen ? 'open' : ''}`} aria-label="Main navigation">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={location.pathname === link.path ? 'active' : ''}
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="navbar-actions">
          {user ? (
            <>
              <span className="navbar-user">{user.first_name || user.username}</span>
              <button onClick={() => { localStorage.removeItem('user'); localStorage.removeItem('access_token'); window.location.href = '/'; }} className="btn btn-secondary btn-sm">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary btn-sm">Log In</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Sign Up</Link>
            </>
          )}
          <button
            className="navbar-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </header>
  );
}

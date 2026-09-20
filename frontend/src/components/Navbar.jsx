import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNav } from '../context/NavContext';
import './Navbar.css';

const NavLinks = [
  { path: '/', label: 'Home' },
  { path: '/events', label: 'Events' },
];

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const { mobileOpen, setMobileOpen } = useNav();
  const location = useLocation();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          EventFlow
        </Link>

        <nav className={`navbar-nav ${mobileOpen ? 'open' : ''}`} aria-label="Main navigation">
          {NavLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={location.pathname === link.path ? 'active' : ''}
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated && (
            <Link
              to={user?.role === 'organizer' ? '/organizer/dashboard' : user?.role === 'admin' ? '/admin/dashboard' : '/user/dashboard'}
              className={location.pathname.includes('dashboard') ? 'active' : ''}
              onClick={() => setMobileOpen(false)}
            >
              Dashboard
            </Link>
          )}
        </nav>

        <div className="navbar-actions">
          {isAuthenticated ? (
            <>
              <span className="navbar-user">{user?.first_name || user?.username}</span>
              <button onClick={logout} className="btn btn-secondary btn-sm">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary btn-sm">
                Log In
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Sign Up
              </Link>
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

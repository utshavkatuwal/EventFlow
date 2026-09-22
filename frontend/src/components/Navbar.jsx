import React, { useState, useEffect } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';
import './Navbar.css';

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/events', label: 'Explore' },
    { path: '/search', label: 'Search' },
  ];
  if (user) {
    const dash = user.role === 'organizer' || user.role === 'admin' ? '/organizer/dashboard' : '/user/dashboard';
    navLinks.push({ path: dash, label: 'Dashboard' });
  }

  const isActive = (path) => path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  const handleLogout = async () => { try { await logout(); } catch {} navigate('/'); };

  return (
    <div className="nav-float-wrap">
      <header className={`navbar-island glass-primary glass-stroke ${scrolled ? 'scrolled' : ''}`}>
        <Link to="/" className="navbar-brand" aria-label="EventFlow Home">
          <span className="brand-mark"><img src={logo} alt="" className="navbar-logo" /></span>
          <span className="navbar-wordmark">EventFlow</span>
        </Link>

        <nav className="navbar-nav" aria-label="Primary">
          {navLinks.map((l) => (
            <Link key={l.path} to={l.path} className={`nav-link ${isActive(l.path) ? 'active' : ''}`}>
              {isActive(l.path) && <span className="nav-pill" />}
              <span className="nav-label">{l.label}</span>
            </Link>
          ))}
        </nav>

        <div className="navbar-actions">
          {user ? (
            <>
              <span className="navbar-user glass-tert">{user.first_name || user.username}</span>
              <button onClick={handleLogout} className="btn btn-ghost btn-sm">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm hide-m">Log In</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
            </>
          )}
          <button className={`navbar-toggle ${mobileOpen ? 'open' : ''}`} onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu" aria-expanded={mobileOpen}>
            <span /><span /><span />
          </button>
        </div>

        <div className={`nav-dropdown glass-secondary ${mobileOpen ? 'open' : ''}`}>
          {navLinks.map((l) => (
            <Link key={l.path} to={l.path} className={`drop-link ${isActive(l.path) ? 'active' : ''}`} onClick={() => setMobileOpen(false)}>{l.label}</Link>
          ))}
          {!user ? (
            <div className="drop-auth">
              <Link to="/login" className="btn btn-ghost btn-sm" onClick={() => setMobileOpen(false)}>Log In</Link>
              <Link to="/register" className="btn btn-primary btn-sm" onClick={() => setMobileOpen(false)}>Get Started</Link>
            </div>
          ) : (
            <button onClick={() => { setMobileOpen(false); handleLogout(); }} className="btn btn-ghost btn-sm" style={{ width: '100%' }}>Logout</button>
          )}
        </div>
      </header>
    </div>
  );
}

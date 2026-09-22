import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';
import '../styles/Footer.css';

export default function Footer() {
  const { user } = useAuth();
  return (
    <footer className="footer-premium">
      <div className="foot-glass glass-secondary glass-stroke">
        <div className="foot-top">
          <div className="foot-brand">
            <span className="foot-mark"><img src={logo} alt="EventFlow" /></span>
            <b>EventFlow</b>
            <p>Discover moments worth remembering — across Nepal.</p>
          </div>
          <nav className="foot-nav" aria-label="Footer">
            <div className="foot-col"><span>Explore</span><Link to="/">Home</Link><Link to="/events">Events</Link><Link to="/search">Search</Link></div>
            <div className="foot-col"><span>Organize</span><Link to="/register">Create event</Link>{user?.role === 'organizer' && <Link to="/organizer/dashboard">Dashboard</Link>}{user?.role === 'admin' && <Link to="/admin/events">Admin</Link>}</div>
            <div className="foot-col"><span>Account</span>{user ? (<><Link to="/user/profile">Profile</Link><Link to="/user/saved">Saved</Link><Link to="/user/dashboard">Dashboard</Link></>) : (<><Link to="/login">Log in</Link><Link to="/register">Sign up</Link></>)}</div>
          </nav>
        </div>
        <div className="foot-bottom"><p>© {new Date().getFullYear()} EventFlow. Crafted with frosted glass.</p><span className="foot-pill glass-tert">● Live</span></div>
      </div>
    </footer>
  );
}

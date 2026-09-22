import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';
import '../styles/Footer.css';

export default function Footer() {
  const { user } = useAuth();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <img src={logo} alt="EventFlow" className="footer-logo" />
        <p className="footer-tagline">Discover events in Nepal.</p>
        <div className="footer-links">
          <Link to="/events">Events</Link>
          <Link to="/search">Search</Link>
          <Link to="/register">Host Event</Link>
          {user && <Link to="/user/dashboard">Dashboard</Link>}
        </div>
        <p className="footer-copy">EventFlow. All rights reserved.</p>
      </div>
    </footer>
  );
}

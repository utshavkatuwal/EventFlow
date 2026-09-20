import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from './Navbar';
import './Footer.css';

export default function Footer() {
  const location = useLocation();
  const { user } = useAuth();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">EventFlow</div>
        <p className="footer-tagline">Discover events in Nepal.</p>
        <div className="footer-links">
          <Link to="/events">Events</Link>
          <Link to="/categories">Categories</Link>
          {user && <Link to="/user/dashboard">Dashboard</Link>}
        </div>
        <p className="footer-copy">EventFlow. All rights reserved.</p>
      </div>
    </footer>
  );
}
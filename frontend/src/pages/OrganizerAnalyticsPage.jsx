import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './OrganizerAnalytics.css';

export default function OrganizerAnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/stats');
        setStats(data?.data || null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Analytics</h1>

        <div className="dashboard-stats">
          <div className="stat"><span className="stat-number">{stats?.total_events || 0}</span><span className="stat-label">Total Events</span></div>
          <div className="stat"><span className="stat-number">{stats?.published_events || 0}</span><span className="stat-label">Published</span></div>
          <div className="stat"><span className="stat-number">{stats?.total_registrations || 0}</span><span className="stat-label">Registrations</span></div>
          <div className="stat"><span className="stat-number">{stats?.checkin_percentage || 0}%</span><span className="stat-label">Check-in Rate</span></div>
        </div>
      </main>
    </>
  );
}
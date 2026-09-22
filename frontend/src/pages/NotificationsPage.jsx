import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import NotificationBadge from '../components/NotificationBadge';
import '../styles/Notifications.css';

export default function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/notifications');
        setNotifications(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    if (user) load();
  }, [user]);

  if (!user) return <p>Please log in to view notifications.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Notifications</h1>

        {notifications.length === 0 ? (
          <p className="empty-state">No notifications yet.</p>
        ) : (
          <div className="notification-list">
            {notifications.map((n) => (
              <div key={n.id} className={`notification-item ${n.is_read ? 'read' : 'unread'}`}>
                <div className="notification-content">
                  <strong>{n.title}</strong>
                  <p>{n.message}</p>
                  <span className="notification-type">{n.type || 'general'}</span>
                </div>
                <span className="notification-date">
                  {new Date(n.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}

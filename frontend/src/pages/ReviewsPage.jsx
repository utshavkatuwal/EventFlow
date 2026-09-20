import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './ReviewsPage.css';

export default function ReviewsPage() {
  const { user } = useAuth();
  const [reviews, setReviews] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!user) return;
      try {
        const data = await apiFetch('/user/reviews');
        setReviews(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  if (!user) return <p>Please log in.</p>;
  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">My Reviews</h1>

        {reviews && reviews.length === 0 ? (
          <p className="empty-state">You have not reviewed any events yet.</p>
        ) : (
          <div className="reviews-list">
            {reviews.map((r) => (
              <div key={r.id} className="review-card">
                <div className="review-rating">{r.rating}/5</div>
                <div className="review-content">
                  <h3>{r.event_title || 'Event'}</h3>
                  <p>{r.comment || 'No comment'}</p>
                  <span className="review-date">{r.created_at?.slice(0, 10)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}

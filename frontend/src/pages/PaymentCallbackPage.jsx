import React, { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import AmbientBackground from '../components/AmbientBackground';
import Loading from '../components/Loading';

export default function PaymentCallbackPage() {
  const [params] = useSearchParams();
  const [state, setState] = useState({ loading: true, ok: false, message: '', ticket: null });
  const ranRef = useRef(false);

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;
    async function run() {
      const provider = (params.get('provider') || '').toUpperCase();
      const reg = params.get('reg');
      const data = params.get('data');
      const pidx = params.get('pidx');
      const failed = params.get('failed');
      if (failed) {
        setState({ loading: false, ok: false, message: 'Payment was cancelled or failed at the provider.', ticket: null });
        return;
      }
      if (!provider || !reg) {
        setState({ loading: false, ok: false, message: 'Invalid callback parameters.', ticket: null });
        return;
      }
      try {
        // eSewa's base64 `data` may arrive with unencoded `+` chars, which URL
        // parsing turns into spaces. Restore them before verification.
        const cleanData = data ? data.replace(/ /g, '+') : data;
        const res = await apiFetch('/payments/verify', {
          method: 'POST',
          body: JSON.stringify({ registration_id: Number(reg), provider, data: cleanData, pidx }),
        });
        setState({ loading: false, ok: true, message: res?.message || 'Payment verified.', ticket: res?.data || null });
      } catch (e) {
        setState({ loading: false, ok: false, message: e.message || 'Verification failed.', ticket: null });
      }
    }
    run();
  }, [params]);

  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="main-content" style={{ maxWidth: 640 }}>
        {state.loading && <Loading />}
        {!state.loading && (
          <div className="card glass-primary" style={{ padding: 32, textAlign: 'center' }}>
            <h1 style={{ fontSize: '1.4rem', marginBottom: 10 }}>
              {state.ok ? 'Payment verified' : 'Payment not completed'}
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 18 }}>{state.message}</p>
            {state.ok && state.ticket?.ticket_code && (
              <div className="ticket-card-qr" style={{ marginBottom: 18 }}>
                <p><strong>Ticket:</strong> <span className="monospace">{state.ticket.ticket_code}</span></p>
              </div>
            )}
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
              {state.ok ? (
                <>
                  {state.ticket?.ticket_id && (
                    <Link to={`/user/tickets/${state.ticket.ticket_id}`} className="btn btn-primary btn-md">View ticket</Link>
                  )}
                  <Link to="/user/tickets" className="btn btn-secondary btn-md">My tickets</Link>
                </>
              ) : (
                <>
                  <Link to="/events" className="btn btn-secondary btn-md">Back to events</Link>
                  <Link to="/user/tickets" className="btn btn-ghost btn-md">My tickets</Link>
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </>
  );
}

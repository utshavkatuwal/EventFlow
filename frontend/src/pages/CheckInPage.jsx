import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from './Navbar';
import Loading from '../components/Loading';
import './CheckIn.css';

export default function CheckInPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [qrInput, setQrInput] = useState('');
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    if (!qrInput.trim()) return;
    setScanning(true);
    try {
      const data = await apiFetch('/checkins/verify', {
        method: 'POST',
        body: JSON.stringify({ qr_token: qrInput, scanned_by_user_id: user?.id }),
      });
      setResult(data);
    } catch (e) {
      setResult({ valid: false, error: 'INVALID_TICKET', message: e.message || 'Verification failed' });
    } finally {
      setScanning(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Check-In</h1>

        <div className="checkin-container">
          <div className="checkin-card">
            <h2>Scan Ticket</h2>
            <p className="checkin-subtitle">Enter the QR token or ticket code to check in an attendee.</p>

            <div className="checkin-input-group">
              <input
                type="text"
                value={qrInput}
                onChange={(e) => setQrInput(e.target.value)}
                placeholder="QR token or ticket code..."
                onKeyDown={(e) => e.key === 'Enter' && handleScan()}
              />
              <button onClick={handleScan} disabled={scanning}>
                {scanning ? 'Scanning...' : 'Scan'}
              </button>
            </div>

            {result && (
              <div className={`checkin-result ${result.valid ? 'valid' : 'invalid'}`}>
                {result.valid ? (
                  <div>
                    <h3>Checked In</h3>
                    <p>{result.message}</p>
                    <p className="checkin-time">{result.ticket?.checked_in_at || result.ticket?.scanned_at || ''}</p>
                    {result.ticket?.ticket_code && (
                      <p className="ticket-code">{result.ticket.ticket_code}</p>
                    )}
                  </div>
                ) : (
                  <div>
                    <h3>{result.error?.replace('_', ' ') || 'Invalid Ticket'}</h3>
                    <p>{result.message}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}

import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/CheckIn.css';

export default function CheckInPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [eventId, setEventId] = useState('');
  const [qrInput, setQrInput] = useState('');
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const scannerRef = useRef(null);
  const eventIdRef = useRef('');
  eventIdRef.current = eventId;

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/organizer/events');
        const items = data?.items || [];
        setEvents(items);
        if (items.length > 0) setEventId(String(items[0].id));
      } catch (e) { console.error(e); } finally { setLoading(false); }
    }
    load();
  }, []);

  const verifyToken = async (token) => {
    if (!token || !eventIdRef.current) return;
    setScanning(true);
    setResult(null);
    try {
      const data = await apiFetch('/organizer/scan', {
        method: 'POST',
        body: JSON.stringify({ qr_token: String(token).trim(), event_id: Number(eventIdRef.current) }),
      });
      setResult({ valid: true, ...data.data, message: data.message });
    } catch (e) {
      const d = e.detail || {};
      setResult({ valid: false, error: d.error || 'INVALID_TICKET', message: d.message || e.message, ...d });
    } finally {
      setScanning(false);
    }
  };

  const handleScan = async () => {
    if (!qrInput.trim() || !eventId) return;
    await verifyToken(qrInput);
    setQrInput('');
  };

  const toggleCamera = async () => {
    if (cameraOn) {
      try { await scannerRef.current?.stop(); } catch {}
      try { await scannerRef.current?.clear(); } catch {}
      scannerRef.current = null;
      setCameraOn(false);
      return;
    }
    setCameraError('');
    try {
      const { Html5Qrcode } = await import('html5-qrcode');
      const scanner = new Html5Qrcode('qr-reader');
      scannerRef.current = scanner;
      await scanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 240, height: 240 } },
        (decoded) => { verifyToken(decoded); },
        () => {}
      );
      setCameraOn(true);
    } catch (err) {
      setCameraError(err?.message || 'Camera unavailable. Type the code manually below.');
    }
  };

  useEffect(() => () => {
    try { scannerRef.current?.stop(); } catch {}
    try { scannerRef.current?.clear(); } catch {}
  }, []);

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Check-In</h1>

        <div className="checkin-container">
          <div className="checkin-card">
            <h2>Scan Ticket</h2>
            <p className="checkin-subtitle">Select the event, then enter the QR token or ticket code.</p>

            <div className="form-group" style={{ marginBottom: 12 }}>
              <label htmlFor="scan-event">Event</label>
              <select id="scan-event" value={eventId} onChange={(e) => setEventId(e.target.value)}>
                {events.map((ev) => (
                  <option key={ev.id} value={ev.id}>{ev.title}</option>
                ))}
              </select>
            </div>

            <div className="checkin-input-group" style={{ marginBottom: 12 }}>
              <button onClick={toggleCamera} disabled={!eventId} className="btn btn-primary btn-md" style={{ flex: 1 }}>
                {cameraOn ? 'Stop camera' : 'Scan with camera'}
              </button>
            </div>
            {cameraError && <p className="muted" role="alert">{cameraError}</p>}
            <div id="qr-reader" style={{ width: '100%', marginBottom: cameraOn ? 12 : 0 }} />

            <div className="checkin-input-group">
              <input
                type="text"
                value={qrInput}
                onChange={(e) => setQrInput(e.target.value)}
                placeholder="QR token or ticket code..."
                onKeyDown={(e) => e.key === 'Enter' && handleScan()}
              />
              <button onClick={handleScan} disabled={scanning || !eventId}>
                {scanning ? 'Scanning...' : 'Scan'}
              </button>
            </div>

            {result && (
              <div className={`checkin-result ${result.valid ? 'valid' : 'invalid'}`}>
                {result.valid ? (
                  <div>
                    <h3>VALID TICKET</h3>
                    <p><strong>Attendee:</strong> {result.attendee || '-'}</p>
                    <p><strong>Event:</strong> {result.event || '-'}</p>
                    <p><strong>Ticket:</strong> <span className="monospace">{result.ticket_code}</span></p>
                    <h3 style={{ marginTop: 10 }}>{result.message || 'ATTENDANCE CONFIRMED'}</h3>
                    <p className="checkin-time">{result.checked_in_at || ''}</p>
                  </div>
                ) : (
                  <div>
                    <h3>{result.error === 'ALREADY_USED' ? 'TICKET ALREADY USED' : (result.error?.replaceAll('_', ' ') || 'Invalid Ticket')}</h3>
                    {result.attendee && <p><strong>Attendee:</strong> {result.attendee}</p>}
                    {result.ticket_code && <p><strong>Ticket:</strong> <span className="monospace">{result.ticket_code}</span></p>}
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

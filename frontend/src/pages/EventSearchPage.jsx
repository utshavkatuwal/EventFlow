import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import AmbientBackground from '../components/AmbientBackground';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';
import Input from '../components/Input';
import '../styles/EventSearch.css';

export default function EventSearchPage() {
  const [sp] = useSearchParams();
  const [query, setQuery] = useState(sp.get('q') || '');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({ category: '', date_from: '', date_to: '', city: sp.get('city') || '' });

  const canSearch = query.trim() || filters.category || filters.date_from || filters.date_to || filters.city;

  const runSearch = async (q, f) => {
    setLoading(true);
    setSearchError('');
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.append('q', q.trim());
      if (f.category) params.append('category', f.category);
      if (f.date_from) params.append('date_from', f.date_from);
      if (f.date_to) params.append('date_to', f.date_to);
      if (f.city) params.append('city', f.city);
      const data = await apiFetch(`/search?${params}`);
      setResults(data?.items || data?.data || []);
    } catch (e) { setSearchError(e.message || 'Search failed.'); setResults([]); } finally { setLoading(false); }
  };

  const handleSearch = (e) => {
    e?.preventDefault();
    if (!canSearch || loading) return;
    runSearch(query, filters);
  };

  const quickPick = (q) => {
    if (loading) return;
    setQuery(q);
    runSearch(q, filters);
  };

  React.useEffect(() => { if (query || filters.city) runSearch(query, filters); // eslint-disable-next-line
  }, []);

  return (
    <>
      <AmbientBackground />
      <Navbar />
      <main className="search-stage">
        <div className="search-console glass-primary glass-stroke glass-sheen">
          <p className="kicker">Search</p>
          <h1>Find your night.</h1>
          <p className="search-sub">Keyword, city, date or category — one search across everything.</p>
          <form onSubmit={handleSearch} className="search-bar" role="search">
            <span className="s-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></span>
            <input
              type="search"
              name="q"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Try ‘jazz’, ‘Pokhara’, ‘workshop’…"
              aria-label="Search events"
              autoComplete="off"
              enterKeyHint="search"
            />
            <button type="submit" disabled={loading || !canSearch} className="btn btn-primary search-go" title={!canSearch ? 'Type a keyword or set a filter first' : 'Search'}>
              {loading ? <span className="btn-spinner" aria-hidden /> : null}
              <span>{loading ? 'Searching' : 'Search'}</span>
            </button>
          </form>
          <button type="button" className={`filter-toggle glass-tert ${showFilters ? 'on' : ''}`} onClick={() => setShowFilters(!showFilters)}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="7" y1="12" x2="17" y2="12"/><line x1="10" y1="18" x2="14" y2="18"/></svg>
            {showFilters ? 'Hide filters' : 'Filters'}
          </button>
          {showFilters && (
            <div className="search-filters-panel">
              <div className="filter-row">
                <Input label="City" id="city" value={filters.city} onChange={(e) => setFilters({ ...filters, city: e.target.value })} placeholder="Kathmandu" />
                <Input label="Category" id="category" value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })} placeholder="Music" />
              </div>
              <div className="filter-row">
                <Input label="From" id="date_from" type="date" value={filters.date_from} onChange={(e) => setFilters({ ...filters, date_from: e.target.value })} />
                <Input label="To" id="date_to" type="date" value={filters.date_to} onChange={(e) => setFilters({ ...filters, date_to: e.target.value })} />
              </div>
            </div>
          )}
        </div>

        {!results && !loading && (
          <div className="search-idle glass-secondary">
            <p>Not sure where to start? Try one of these:</p>
            <div className="idle-picks">
              {['Music', 'Technology', 'Workshop', 'Sports', 'Arts'].map((c) => (
                <button key={c} type="button" className="dchip" onClick={() => quickPick(c)}>{c}</button>
              ))}
            </div>
          </div>
        )}

        {searchError && <div className="form-error" role="alert" style={{ marginBottom: 16 }}>{searchError}</div>}

        {results && (
          <div className="search-results">
            <p className="results-count glass-tert">{results.length} result{results.length !== 1 ? 's' : ''}</p>
            {results.length === 0 ? (
              <div className="empty-glass glass-secondary"><h3>No matches</h3><p>Try a broader keyword or remove a filter.</p></div>
            ) : (
              <div className="ev-grid">
                {results.map((ev) => <EventCard key={ev.id} event={ev} />)}
              </div>
            )}
          </div>
        )}
        <Footer />
      </main>
    </>
  );
}

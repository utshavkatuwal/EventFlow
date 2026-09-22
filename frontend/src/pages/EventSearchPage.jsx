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
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({ category: '', date_from: '', date_to: '', city: sp.get('city') || '' });

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim() && !filters.category && !filters.date_from && !filters.date_to && !filters.city) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ q: query });
      if (filters.category) params.append('category', filters.category);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.city) params.append('city', filters.city);
      const data = await apiFetch(`/search?${params}`);
      setResults(data?.items || data?.data || []);
    } catch (e) { console.error(e); setResults([]); } finally { setLoading(false); }
  };

  React.useEffect(() => { if (query || filters.city) handleSearch(); // eslint-disable-next-line
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
          <form onSubmit={handleSearch} className="search-bar">
            <span className="s-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></span>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Try ‘jazz’, ‘Pokhara’, ‘workshop’…" aria-label="Search events" />
            <button type="submit" disabled={loading} className="btn btn-primary">{loading ? 'Searching…' : 'Search'}</button>
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

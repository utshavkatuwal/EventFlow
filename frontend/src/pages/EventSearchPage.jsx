import React, { useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import Input from '../components/Input';
import SimpleEventCard from '../components/SimpleEventCard';
import '../styles/EventSearch.css';

export default function EventSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({ category: '', date_from: '', date_to: '', city: '' });

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim() && !filters.category && !filters.date_from && !filters.date_to && !filters.city) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ q: query });
      if (filters.category) params.append('category', filters.category);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.city) params.append('city', filters.city);
      const data = await apiFetch(`/search?${params}`);
      setResults(data?.items || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="search-page">
          <h1 className="search-title">Search Events</h1>

          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by title, location, category..."
                aria-label="Search events"
              />
              <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowFilters(!showFilters)}>
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </form>

          {showFilters && (
            <div className="search-filters">
              <div className="filter-row">
                <Input label="Category" id="category" value={filters.category} onChange={(e) => setFilters({...filters, category: e.target.value})} placeholder="All categories" />
                <Input label="City" id="city" value={filters.city} onChange={(e) => setFilters({...filters, city: e.target.value})} placeholder="All cities" />
              </div>
              <div className="filter-row">
                <Input label="Date From" id="date_from" type="date" value={filters.date_from} onChange={(e) => setFilters({...filters, date_from: e.target.value})} />
                <Input label="Date To" id="date_to" type="date" value={filters.date_to} onChange={(e) => setFilters({...filters, date_to: e.target.value})} />
              </div>
            </div>
          )}

          {loading && <Loading />}
          {results && results.length === 0 && !loading && <p className="empty-state">No events found matching your criteria.</p>}
          {results && results.length > 0 && (
            <div className="search-results">
              <p className="results-count">{results.length} event{results.length !== 1 ? 's' : ''} found</p>
              <div className="events-grid">
                {results.map((ev) => (
                  <SimpleEventCard key={ev.id} event={ev} />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
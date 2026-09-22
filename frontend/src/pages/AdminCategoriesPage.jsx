import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/AdminCategories.css';

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newCategory, setNewCategory] = useState({ name: '', description: '', icon: '' });

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/categories');
        setCategories(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await apiFetch('/categories', { method: 'POST', body: JSON.stringify(newCategory) });
      setNewCategory({ name: '', description: '', icon: '' });
      // Refresh
      const data = await apiFetch('/categories');
      setCategories(data?.items || []);
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - Categories</h1>

        <form onSubmit={handleAdd} className="admin-category-form">
          <div className="form-row">
            <div className="form-group">
              <label>Name</label>
              <input type="text" value={newCategory.name} onChange={(e) => setNewCategory({...newCategory, name: e.target.value})} required />
            </div>
            <div className="form-group">
              <label>Icon</label>
              <input type="text" value={newCategory.icon} onChange={(e) => setNewCategory({...newCategory, icon: e.target.value})} placeholder="emoji or class" />
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <input type="text" value={newCategory.description} onChange={(e) => setNewCategory({...newCategory, description: e.target.value})} />
          </div>
          <button type="submit" className="btn btn-primary">Add Category</button>
        </form>

        <div className="admin-categories-table">
          <table className="data-table">
            <thead><tr><th>ID</th><th>Name</th><th>Slug</th><th>Description</th><th>Icon</th></tr></thead>
            <tbody>
              {categories?.map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.slug}</td>
                  <td>{c.description || '-'}</td>
                  <td>{c.icon || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
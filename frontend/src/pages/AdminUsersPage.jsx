import React, { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import Navbar from '../components/Navbar';
import Loading from '../components/Loading';
import '../styles/AdminUsers.css';

export default function AdminUsersPage() {
  const [users, setUsers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch('/users');
        setUsers(data?.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSuspend = async (userId, currentStatus) => {
    try {
      await apiFetch(`/users/${userId}/suspend`, { method: 'PATCH' });
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: !currentStatus } : u));
    } catch (e) {
      alert(e.message);
    }
  };

  if (loading) return <Loading />;

  return (
    <>
      <Navbar />
      <main className="main-content">
        <h1 className="dashboard-title">Admin - User Management</h1>

        <div className="admin-users-table">
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Email</th><th>Username</th><th>Name</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              {users?.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.email}</td>
                  <td>{u.username}</td>
                  <td>{u.first_name || ''} {u.last_name || ''}</td>
                  <td>{u.is_active ? 'Active' : 'Suspended'}</td>
                  <td>
                    <button
                      className={`btn btn-sm ${u.is_active ? 'btn-warning' : 'btn-success'}`}
                      onClick={() => handleSuspend(u.id, u.is_active)}
                    >
                      {u.is_active ? 'Suspend' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
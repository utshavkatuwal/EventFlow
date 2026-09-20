import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function OrganizerOnly({ children }) {
  const { user } = useAuth();
  if (user?.role !== 'organizer' && user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  return children;
}

export function AdminOnly({ children }) {
  const { user } = useAuth();
  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  return children;
}

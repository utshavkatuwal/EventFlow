import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { homeForUser } from '../utils/roles';
import Loading from './Loading';

/** /dashboard → role home. Fixes "clicking Dashboard does nothing". */
export default function RoleHome() {
  const { user, isAuthenticated, authReady } = useAuth();
  if (!authReady) return <Loading />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={homeForUser(user)} replace />;
}

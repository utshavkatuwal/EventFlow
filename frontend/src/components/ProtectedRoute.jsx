import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getRole, homeFor } from '../utils/roles';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated, authReady } = useAuth();
  const location = useLocation();

  if (!authReady) return null;
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const wanted = allowedRoles.map((r) => String(r).toLowerCase());
    const role = getRole(user);
    if (!wanted.includes(role)) {
      // Wrong role: send to their OWN dashboard, never a foreign one.
      return <Navigate to={homeFor(role)} replace />;
    }
  }

  return children;
}

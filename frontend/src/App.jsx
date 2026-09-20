import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { NavProvider } from './context/NavContext';
import { ApiProvider } from './context/ApiContext';
import RequireAuth from './components/RequireAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Loading from './components/Loading';

const HomePage = lazy(() => import('./pages/HomePage.jsx'));
const EventsPage = lazy(() => import('./pages/EventsPage.jsx'));
const EventDetailPage = lazy(() => import('./pages/EventDetailPage.jsx'));
const LoginPage = lazy(() => import('./pages/LoginPage.jsx'));
const RegisterPage = lazy(() => import('./pages/RegisterPage.jsx'));
const UserDashboardPage = lazy(() => import('./pages/UserDashboardPage.jsx'));
const OrganizerDashboardPage = lazy(() => import('./pages/OrganizerDashboardPage.jsx'));
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage.jsx'));
const TicketPage = lazy(() => import('./pages/TicketPage.jsx'));
const CheckInPage = lazy(() => import('./pages/CheckInPage.jsx'));
const ProfilePage = lazy(() => import('./pages/ProfilePage.jsx'));

function AppRoutes() {
  const { user, isAuthenticated } = useAuth();

  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/events" element={<EventsPage />} />
        <Route path="/events/:id" element={<EventDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/user/dashboard"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['user']}>
                <UserDashboardPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/user/tickets/:id"
          element={
            <RequireAuth>
              <TicketPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />

        <Route
          path="/organizer/dashboard"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <OrganizerDashboardPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/organizer/checkin"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <CheckInPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />

        <Route
          path="/admin/dashboard"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboardPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <ApiProvider>
      <NavProvider>
        <AppRoutes />
      </NavProvider>
    </ApiProvider>
  );
}

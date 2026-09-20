import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { NavProvider } from './context/NavContext';
import { ApiProvider } from './context/ApiContext';
import RequireAuth from './components/RequireAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Loading from './components/Loading';
import Footer from './components/Footer';

// Lazy loaded pages
const HomePage = lazy(() => import('./pages/HomePage'));
const EventsPage = lazy(() => import('./pages/EventsPage'));
const EventDetailPage = lazy(() => import('./pages/EventDetailPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const UserDashboardPage = lazy(() => import('./pages/UserDashboardPage'));
const OrganizerDashboardPage = lazy(() => import('./pages/OrganizerDashboardPage'));
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'));
const TicketPage = lazy(() => import('./pages/TicketPage'));
const CheckInPage = lazy(() => import('./pages/CheckInPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const CreateEventPage = lazy(() => import('./pages/CreateEventPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const DashboardShell = lazy(() => import('./components/DashboardShell'));

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

        <Route path="/user/dashboard" element={<RequireAuth><ProtectedRoute allowedRoles={['user']}><UserDashboardPage /></ProtectedRoute></RequireAuth>} />
        <Route path="/user/tickets/:id" element={<RequireAuth><TicketPage /></RequireAuth>} />
        <Route path="/user/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/user/notifications" element={<RequireAuth><NotificationsPage /></RequireAuth>} />

        <Route path="/organizer/dashboard" element={<RequireAuth><ProtectedRoute allowedRoles={['organizer', 'admin']}><OrganizerDashboardPage /></ProtectedRoute></RequireAuth>} />
        <Route path="/organizer/create-event" element={<RequireAuth><ProtectedRoute allowedRoles={['organizer', 'admin']}><CreateEventPage /></ProtectedRoute></RequireAuth>} />
        <Route path="/organizer/checkin" element={<RequireAuth><ProtectedRoute allowedRoles={['organizer', 'admin']}><CheckInPage /></ProtectedRoute></RequireAuth>} />
        <Route path="/organizer/notifications" element={<RequireAuth><ProtectedRoute allowedRoles={['organizer', 'admin']}><NotificationsPage /></ProtectedRoute></RequireAuth>} />

        <Route path="/admin/dashboard" element={<RequireAuth><ProtectedRoute allowedRoles={['admin']}><AdminDashboardPage /></ProtectedRoute></RequireAuth>} />
        <Route path="/admin/notifications" element={<RequireAuth><ProtectedRoute allowedRoles={['admin']}><NotificationsPage /></ProtectedRoute></RequireAuth>} />

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

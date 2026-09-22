import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import { NavProvider } from './context/NavContext.jsx';
import RequireAuth from './components/RequireAuth.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Loading from './components/Loading.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import ScrollToTop from './components/ScrollToTop.jsx';

// Lazy loaded pages
const HomePage = React.lazy(() => import('./pages/HomePage'));
const EventsPage = React.lazy(() => import('./pages/EventsPage'));
const EventDetailPage = React.lazy(() => import('./pages/EventDetailPage'));
const LoginPage = React.lazy(() => import('./pages/LoginPage'));
const RegisterPage = React.lazy(() => import('./pages/RegisterPage'));
const UserDashboardPage = React.lazy(() => import('./pages/UserDashboardPage'));
const MyTicketsPage = React.lazy(() => import('./pages/MyTicketsPage'));
const SavedEventsPage = React.lazy(() => import('./pages/SavedEventsPage'));
const ReviewsPage = React.lazy(() => import('./pages/ReviewsPage'));
const UpcomingEventsPage = React.lazy(() => import('./pages/UpcomingEventsPage'));
const PastEventsPage = React.lazy(() => import('./pages/PastEventsPage'));
const ProfilePage = React.lazy(() => import('./pages/ProfilePage'));
const ProfileEditPage = React.lazy(() => import('./pages/ProfileEditPage'));
const TicketDetailPage = React.lazy(() => import('./pages/TicketDetailPage'));
const CreateEventPage = React.lazy(() => import('./pages/CreateEventPage'));
const NotificationsPage = React.lazy(() => import('./pages/NotificationsPage'));
const CheckInPage = React.lazy(() => import('./pages/CheckInPage'));
const EventSearchPage = React.lazy(() => import('./pages/EventSearchPage'));
const CategoryEventsPage = React.lazy(() => import('./pages/CategoryEventsPage'));
const OrganizerDashboardPage = React.lazy(() => import('./pages/OrganizerDashboardPage'));
const OrganizerMyEventsPage = React.lazy(() => import('./pages/OrganizerMyEventsPage'));
const OrganizerRegistrationsPage = React.lazy(() => import('./pages/OrganizerRegistrationsPage'));
const OrganizerAnalyticsPage = React.lazy(() => import('./pages/OrganizerAnalyticsPage'));
const OrganizerProfilePage = React.lazy(() => import('./pages/OrganizerProfilePage'));
const AdminDashboardPage = React.lazy(() => import('./pages/AdminDashboardPage'));
const AdminEventsPage = React.lazy(() => import('./pages/AdminEventsPage'));
const AdminUsersPage = React.lazy(() => import('./pages/AdminUsersPage'));
const AdminOrganizersPage = React.lazy(() => import('./pages/AdminOrganizersPage'));
const AdminReportsPage = React.lazy(() => import('./pages/AdminReportsPage'));
const AdminAuditLogsPage = React.lazy(() => import('./pages/AdminAuditLogsPage'));
const AdminCategoriesPage = React.lazy(() => import('./pages/AdminCategoriesPage'));

function AppRoutes() {
  const { user, isAuthenticated } = useAuth();

  return (
    <ErrorBoundary>
      <React.Suspense fallback={<Loading />}>
        <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/events" element={<EventsPage />} />
        <Route path="/events/:id" element={<EventDetailPage />} />
        <Route path="/search" element={<EventSearchPage />} />
        <Route path="/categories/:id" element={<CategoryEventsPage />} />
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
              <TicketDetailPage />
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
          path="/user/profile/edit"
          element={
            <RequireAuth>
              <ProfileEditPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/saved"
          element={
            <RequireAuth>
              <SavedEventsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/reviews"
          element={
            <RequireAuth>
              <ReviewsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/upcoming"
          element={
            <RequireAuth>
              <UpcomingEventsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/past"
          element={
            <RequireAuth>
              <PastEventsPage />
            </RequireAuth>
          }
        />
        <Route
          path="/user/notifications"
          element={
            <RequireAuth>
              <NotificationsPage />
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
          path="/organizer/create-event"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <CreateEventPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/organizer/my-events"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <OrganizerMyEventsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/organizer/registrations"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <OrganizerRegistrationsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/organizer/analytics"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <OrganizerAnalyticsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/organizer/profile"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <OrganizerProfilePage />
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
          path="/organizer/notifications"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['organizer', 'admin']}>
                <NotificationsPage />
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
        <Route
          path="/admin/events"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminEventsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/users"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminUsersPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/organizers"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminOrganizersPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/reports"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminReportsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/audit-logs"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminAuditLogsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/categories"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminCategoriesPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/notifications"
          element={
            <RequireAuth>
              <ProtectedRoute allowedRoles={['admin']}>
                <NotificationsPage />
              </ProtectedRoute>
            </RequireAuth>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </React.Suspense>
  </ErrorBoundary>
);
}

export default function App() {
  return (
    <NavProvider>
      <ScrollToTop />
      <AppRoutes />
    </NavProvider>
  );
}
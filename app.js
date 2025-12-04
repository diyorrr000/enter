# enterprise_erp/frontend/src/App.js
"""
React frontend for Enterprise ERP System
"""

import React, { useState, useEffect, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';
import { QueryClient, QueryClientProvider } from 'react-query';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { CompanyProvider } from './contexts/CompanyContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Layout Components
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';
import AdminLayout from './layouts/AdminLayout';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Dashboard Pages
import Dashboard from './pages/dashboard/Dashboard';
import Overview from './pages/dashboard/Overview';
import Analytics from './pages/dashboard/Analytics';
import Reports from './pages/dashboard/Reports';

// HR Pages
import Employees from './pages/hr/Employees';
import EmployeeDetail from './pages/hr/EmployeeDetail';
import Attendance from './pages/hr/Attendance';
import LeaveManagement from './pages/hr/LeaveManagement';
import Payroll from './pages/hr/Payroll';
import Recruitment from './pages/hr/Recruitment';

// Finance Pages
import Accounting from './pages/finance/Accounting';
import Invoices from './pages/finance/Invoices';
import Payments from './pages/finance/Payments';
import Expenses from './pages/finance/Expenses';
import Budgeting from './pages/finance/Budgeting';
import FinancialReports from './pages/finance/FinancialReports';

// Sales Pages
import Customers from './pages/sales/Customers';
import SalesOrders from './pages/sales/SalesOrders';
import Quotations from './pages/sales/Quotations';
import SalesAnalytics from './pages/sales/SalesAnalytics';
import CRM from './pages/sales/CRM';

// Inventory Pages
import Products from './pages/inventory/Products';
import StockManagement from './pages/inventory/StockManagement';
import Warehouse from './pages/inventory/Warehouse';
import Suppliers from './pages/inventory/Suppliers';
import PurchaseOrders from './pages/inventory/PurchaseOrders';

// Project Pages
import Projects from './pages/projects/Projects';
import ProjectDetail from './pages/projects/ProjectDetail';
import Tasks from './pages/projects/Tasks';
import TimeTracking from './pages/projects/TimeTracking';

// Settings Pages
import CompanySettings from './pages/settings/CompanySettings';
import UserSettings from './pages/settings/UserSettings';
import SystemSettings from './pages/settings/SystemSettings';
import AuditLogs from './pages/settings/AuditLogs';

// Components
import PrivateRoute from './components/routes/PrivateRoute';
import AdminRoute from './components/routes/AdminRoute';
import Loading from './components/common/Loading';
import ErrorBoundary from './components/common/ErrorBoundary';

// Services
import api from './services/api';
import { setupInterceptors } from './services/interceptors';

// Theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          border: '1px solid #e0e0e0',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Setup axios interceptors
setupInterceptors();

function App() {
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    // Initialize app
    const initApp = async () => {
      try {
        // Check authentication status
        const token = localStorage.getItem('access_token');
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Fetch user data if token exists
          const userData = await api.get('/users/me/');
          // Store user data in context or state
        }
        
        setInitialized(true);
      } catch (error) {
        console.error('App initialization error:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      } finally {
        setLoading(false);
      }
    };

    initApp();
  }, []);

  if (loading) {
    return <Loading fullScreen />;
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <SnackbarProvider 
            maxSnack={3} 
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            autoHideDuration={3000}
          >
            <AuthProvider>
              <CompanyProvider>
                <NotificationProvider>
                  <Router>
                    <Routes>
                      {/* Auth Routes */}
                      <Route path="/auth" element={<AuthLayout />}>
                        <Route path="login" element={<Login />} />
                        <Route path="register" element={<Register />} />
                        <Route path="forgot-password" element={<ForgotPassword />} />
                        <Route path="reset-password" element={<ResetPassword />} />
                      </Route>

                      {/* Main App Routes */}
                      <Route path="/" element={
                        <PrivateRoute>
                          <MainLayout />
                        </PrivateRoute>
                      }>
                        {/* Dashboard */}
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="dashboard" element={<Dashboard />}>
                          <Route index element={<Overview />} />
                          <Route path="analytics" element={<Analytics />} />
                          <Route path="reports" element={<Reports />} />
                        </Route>

                        {/* HR Management */}
                        <Route path="hr">
                          <Route path="employees" element={<Employees />} />
                          <Route path="employees/:id" element={<EmployeeDetail />} />
                          <Route path="attendance" element={<Attendance />} />
                          <Route path="leave" element={<LeaveManagement />} />
                          <Route path="payroll" element={<Payroll />} />
                          <Route path="recruitment" element={<Recruitment />} />
                        </Route>

                        {/* Finance */}
                        <Route path="finance">
                          <Route path="accounting" element={<Accounting />} />
                          <Route path="invoices" element={<Invoices />} />
                          <Route path="payments" element={<Payments />} />
                          <Route path="expenses" element={<Expenses />} />
                          <Route path="budgeting" element={<Budgeting />} />
                          <Route path="reports" element={<FinancialReports />} />
                        </Route>

                        {/* Sales */}
                        <Route path="sales">
                          <Route path="customers" element={<Customers />} />
                          <Route path="orders" element={<SalesOrders />} />
                          <Route path="quotations" element={<Quotations />} />
                          <Route path="analytics" element={<SalesAnalytics />} />
                          <Route path="crm" element={<CRM />} />
                        </Route>

                        {/* Inventory */}
                        <Route path="inventory">
                          <Route path="products" element={<Products />} />
                          <Route path="stock" element={<StockManagement />} />
                          <Route path="warehouse" element={<Warehouse />} />
                          <Route path="suppliers" element={<Suppliers />} />
                          <Route path="purchase-orders" element={<PurchaseOrders />} />
                        </Route>

                        {/* Projects */}
                        <Route path="projects">
                          <Route path="list" element={<Projects />} />
                          <Route path=":id" element={<ProjectDetail />} />
                          <Route path="tasks" element={<Tasks />} />
                          <Route path="time-tracking" element={<TimeTracking />} />
                        </Route>

                        {/* Settings */}
                        <Route path="settings">
                          <Route path="company" element={
                            <AdminRoute>
                              <CompanySettings />
                            </AdminRoute>
                          } />
                          <Route path="user" element={<UserSettings />} />
                          <Route path="system" element={
                            <AdminRoute>
                              <SystemSettings />
                            </AdminRoute>
                          } />
                          <Route path="audit-logs" element={
                            <AdminRoute>
                              <AuditLogs />
                            </AdminRoute>
                          } />
                        </Route>
                      </Route>

                      {/* Admin Routes */}
                      <Route path="/admin" element={
                        <AdminRoute>
                          <AdminLayout />
                        </AdminRoute>
                      }>
                        {/* Admin specific routes will be added here */}
                      </Route>

                      {/* Catch all route */}
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </Router>
                </NotificationProvider>
              </CompanyProvider>
            </AuthProvider>
          </SnackbarProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

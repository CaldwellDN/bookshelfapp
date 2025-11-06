import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { isTokenValid } from './auth';
import { fetchAPI } from './apiClient';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

  useEffect(() => {
    async function checkAuth() {
      const accessToken = localStorage.getItem('access_token');

      if (isTokenValid(accessToken)) {
        setIsAuthorized(true);
        return;
      }

      // Try refreshing
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        setIsAuthorized(false);
        return;
      }

      try {
        const refreshResponse = await fetchAPI("http://localhost:8000/auth/refresh", {
          method: "POST",
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          setIsAuthorized(true);
        } else {
          setIsAuthorized(false);
        }
      } catch (err) {
        console.error("Error refreshing token:", err);
        setIsAuthorized(false);
      }
    }

    checkAuth();
  }, []);

  // Show nothing (or a spinner) until check finishes
  if (isAuthorized === null) return null;

  return isAuthorized ? <>{children}</> : <Navigate to="/" replace />;
}

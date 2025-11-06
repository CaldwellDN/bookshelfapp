import React, { useEffect, useState } from 'react';
import { getUserNameFromToken, getIDFromToken } from '../auth';

export default function UserMenu() {
  const [username, setUsername] = useState<string | null>(null);
  const [ID, setID] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const name = getUserNameFromToken(token);
    setUsername(name);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const id = getIDFromToken(token);
    setID(id);
  }, []);

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await fetch("http://localhost:8000/auth/logout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (err) {
        console.error("Logout request failed:", err);
      }
    }

    // Clear client tokens regardless
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Redirect to login page
    window.location.reload();
  };

  return (
    <div style={{
      position: "absolute",
      top: "10px",
      right: "20px",
      display: "flex",
      alignItems: "center",
      gap: "10px"
    }}>
      {username && <span>Welcome, <b>{username} | {ID}</b></span>}
      {username && <button onClick={handleLogout}>Logout</button>}
    </div>
  );
}

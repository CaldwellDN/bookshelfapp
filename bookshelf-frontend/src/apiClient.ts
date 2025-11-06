import { isTokenValid } from "./auth";

const API_BASE_URL = 'http://localhost:8000/';

export async function fetchAPI(endpoint: string, options: RequestInit = {}): Promise<Response> {
    let accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    if (!accessToken) {
        throw new Error("No access token available.");
    }

    if (!isTokenValid(accessToken) && refreshToken) {
        const refreshed = await refreshAccessToken(refreshToken);
        if (!refreshed) {
            throw new Error("Unable to refresh access token.");
        }
        accessToken = localStorage.getItem("access_token");
    }

    const headers = new Headers(options.headers || {});
    headers.set("authorization", `Bearer ${accessToken}`);
  
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  
    if (response.status === 401) {
      if (refreshToken) {
        const refreshed = await refreshAccessToken(refreshToken);
        if (refreshed) {
          const retryHeaders = new Headers(options.headers || {});
          retryHeaders.set("authorization", `Bearer ${localStorage.getItem("access_token")}`);
          return await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers: retryHeaders });
        }
      }
      throw new Error("Unauthorized");
    }
  
    return response;
}

async function refreshAccessToken(refreshToken: string): Promise<boolean> {
    try {
        const refreshResponse = await fetch(`${API_BASE_URL}auth/refresh`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ refresh_token: refreshToken})
        });
    
        if(!refreshResponse.ok) {
            return false;
        }
    
        const data = await refreshResponse.json();
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        return true;
    } catch (error) {
        console.error(`refreshAccessToken error: ${error}`);
        return false;
    }
    
}
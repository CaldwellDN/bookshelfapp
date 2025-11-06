import { jwtDecode, type JwtPayload } from 'jwt-decode';

interface MyJwtPayload extends JwtPayload {
  username?: string;
  sub?: string;
}

export function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  try {
    const decodedToken = jwtDecode<MyJwtPayload>(token);
    if (!decodedToken.exp) return false;
    return (Date.now() / 1000) < decodedToken.exp;
  } catch (error) {
    console.log(`Error: ${error}`);
    return false;
  }
}

export function getUserNameFromToken(token: string | null): string | null {
  if (!token) return null;
  try {
    const decoded = jwtDecode<MyJwtPayload>(token);
    return decoded.username ?? null;
  } catch {
    return null;
  }
}

export function getIDFromToken(token: string | null): string | null {
    if (!token) return null;
    try {
      const decoded = jwtDecode<MyJwtPayload>(token);
      return decoded.sub ?? null;
    } catch {
      return null;
    }
  }

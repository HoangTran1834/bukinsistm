// Simple API helper for backend requests
const API_URL = 'http://localhost:8000/api';

export async function signup(data: any) {
  const res = await fetch(`${API_URL}/auth/signup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function login(data: any) {
  const res = await fetch(`${API_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getProfile(token: string) {
  const res = await fetch(`${API_URL}/user/profile/`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return res.json();
}

export async function getBookings(token: string) {
  const res = await fetch(`${API_URL}/booking/`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return res.json();
}

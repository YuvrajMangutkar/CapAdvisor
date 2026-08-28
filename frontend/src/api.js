// src/api.js — Centralized API calls

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

export async function getCatalog() {
  const [categories, districts, branches] = await Promise.all([
    fetch(`${BASE}/categories`),
    fetch(`${BASE}/districts`),
    fetch(`${BASE}/branches`),
  ]);
  if (!categories.ok || !districts.ok || !branches.ok) {
    throw new Error('Unable to load the current CAP college catalog');
  }
  return {
    categories: await categories.json(),
    districts: (await districts.json()).districts,
    branches: (await branches.json()).branches,
  };
}

export async function generateList(payload) {
  const res = await fetch(`${BASE}/generate-list`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function compareTop5Colleges(payload) {
  const res = await fetch(`${BASE}/compare-top5`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Comparison request failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function sendContact(payload) {
  const res = await fetch(`${BASE}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({ detail: 'Unable to send message' }));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

export function getExcelUrl(params) {
  const q = new URLSearchParams({
    percentile: params.percentile,
    category_code: params.category_code,
    preferred_districts: (params.preferred_districts || []).join(','),
    preferred_branch_codes: (params.preferred_branch_codes || []).join(','),
  });
  return `${BASE}/export/excel?${q}`;
}

export function getPdfUrl(params) {
  const q = new URLSearchParams({
    percentile: params.percentile,
    category_code: params.category_code,
    preferred_districts: (params.preferred_districts || []).join(','),
    preferred_branch_codes: (params.preferred_branch_codes || []).join(','),
  });
  return `${BASE}/export/pdf?${q}`;
}

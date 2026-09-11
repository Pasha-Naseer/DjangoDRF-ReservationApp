const BASE_URL = "/api";

export function getTokens() {
  return {
    access: localStorage.getItem("access"),
    refresh: localStorage.getItem("refresh"),
  };
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem("access", access);
  if (refresh) localStorage.setItem("refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

async function refreshAccessToken() {
  const { refresh } = getTokens();
  if (!refresh) return null;
  const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    clearTokens();
    return null;
  }
  const data = await res.json();
  setTokens({ access: data.access });
  return data.access;
}

/**
 * apiFetch(path, { method, body, isMultipart })
 * - body: plain object. Sent as JSON, or as FormData if isMultipart is true
 *   (needed for the receipt upload on reservation create).
 * - Automatically attaches the JWT access token and retries once after a
 *   silent refresh if the access token has expired (401).
 */
export async function apiFetch(path, { method = "GET", body, isMultipart = false } = {}) {
  const doFetch = (accessToken) => {
    const headers = {};
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

    let fetchBody;
    if (body !== undefined) {
      if (isMultipart) {
        fetchBody = new FormData();
        Object.entries(body).forEach(([k, v]) => fetchBody.append(k, v));
      } else {
        headers["Content-Type"] = "application/json";
        fetchBody = JSON.stringify(body);
      }
    }

    return fetch(`${BASE_URL}${path}`, { method, headers, body: fetchBody });
  };

  let { access } = getTokens();
  let res = await doFetch(access);

  if (res.status === 401 && access) {
    const newAccess = await refreshAccessToken();
    if (newAccess) res = await doFetch(newAccess);
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error("API error");
    err.data = data;
    err.status = res.status;
    throw err;
  }
  return data;
}

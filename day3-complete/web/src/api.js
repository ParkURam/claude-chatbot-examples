// src/api.js — 서버 주소는 한 곳에서만 정한다.
// 개발 중에는 VITE_API_BASE=http://localhost:8000 으로 띄우고,
// 빌드해서 FastAPI 가 서빙할 때는 비워 두면 같은 출처로 나간다.
const API_BASE = import.meta.env.VITE_API_BASE ?? '';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}/api${path}`, options);
  if (!response.ok) {
    throw new Error(`서버 오류: ${response.status}`);
  }
  return response.json();
}

export function createConversation() {
  return request('/conversations', { method: 'POST' });
}

export function sendQuestion(conversationId, question) {
  return request(`/chat/${conversationId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
}

export function fetchMessages(conversationId) {
  return request(`/conversations/${conversationId}/messages`);
}

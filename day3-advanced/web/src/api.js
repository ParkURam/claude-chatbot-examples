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

const API_BASE_FOR_STREAM = import.meta.env.VITE_API_BASE ?? '';
const LINE_SEP = ' ';   // 서버가 답변 속 줄바꿈을 이 문자로 바꿔 보낸다

// 조각이 도착할 때마다 onChunk(누적된 답변)를 부른다.
export async function streamQuestion(conversationId, question, { onChunk, signal }) {
  const response = await fetch(
    `${API_BASE_FOR_STREAM}/api/chat/${conversationId}/stream`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal,
    },
  );
  if (!response.ok) {
    throw new Error(`서버 오류: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let answer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    // 조각이 이벤트 경계에서 잘려 도착할 수 있으므로 버퍼에 모았다가 자른다.
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() ?? '';

    for (const event of events) {
      if (event.startsWith('event: error')) {
        throw new Error(event.split('data: ')[1] ?? '스트리밍 오류');
      }
      if (event.startsWith('event: done')) continue;
      if (event.startsWith('data: ')) {
        answer += event.slice('data: '.length).split(LINE_SEP).join('\n');
        onChunk(answer);
      }
    }
  }
  return answer;
}

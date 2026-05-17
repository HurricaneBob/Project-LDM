// Frontend ↔ backend contract for the chat endpoint.
//
// POST {VITE_API_BASE_URL}/api/chat
// Body: { sessionId, message, history }
// Response: { sessionId, personaResponses, parameterDeltas, sessionTitle?, situationBrief?, meta? }

const BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').replace(/\/+$/, '');

function assertApiBaseUrl() {
  if (!BASE) {
    throw new Error(
      'VITE_API_BASE_URL이 설정되지 않았습니다. .env 파일에 백엔드 URL을 설정하세요 (예: VITE_API_BASE_URL=http://localhost:5000).'
    );
  }
}

function apiUrl(path) {
  assertApiBaseUrl();
  return `${BASE}${path}`;
}

async function apiPost(path, body) {
  let res;
  try {
    res = await fetch(apiUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch (e) {
    const detail = e?.message || String(e);
    if (detail === 'Failed to fetch' || detail.includes('NetworkError')) {
      throw new Error(`네트워크 오류 — 백엔드에 연결할 수 없습니다 (${BASE})`);
    }
    throw new Error(detail);
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      if (err?.error) detail = err.error;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  return res.json();
}

function validateChatResponse(data) {
  if (!data || typeof data !== 'object') {
    throw new Error('응답 형식 오류: JSON 객체가 아닙니다.');
  }
  if (!data.sessionId || typeof data.sessionId !== 'string') {
    throw new Error('응답 형식 오류: sessionId가 없습니다.');
  }
  if (!Array.isArray(data.personaResponses)) {
    throw new Error('응답 형식 오류: personaResponses 배열이 없습니다.');
  }
  for (let i = 0; i < data.personaResponses.length; i++) {
    const r = data.personaResponses[i];
    if (!r || typeof r !== 'object') {
      throw new Error(`응답 형식 오류: personaResponses[${i}]가 잘못되었습니다.`);
    }
    if (!r.personaId || typeof r.personaId !== 'string') {
      throw new Error(`응답 형식 오류: personaResponses[${i}].personaId가 없습니다.`);
    }
    if (typeof r.message !== 'string') {
      throw new Error(`응답 형식 오류: personaResponses[${i}].message가 문자열이 아닙니다.`);
    }
  }
  if (
    data.parameterDeltas != null &&
    (typeof data.parameterDeltas !== 'object' || Array.isArray(data.parameterDeltas))
  ) {
    throw new Error('응답 형식 오류: parameterDeltas가 객체가 아닙니다.');
  }
  return data;
}

export async function chat({ sessionId, message, history }) {
  const data = await apiPost('/api/chat', { sessionId, message, history });
  return validateChatResponse(data);
}

export async function fetchFinalEvaluation(sessionId) {
  if (!sessionId) return null;
  assertApiBaseUrl();
  return apiPost('/api/evaluation/final', { session_id: sessionId });
}

export function getApiBaseUrl() {
  return BASE;
}

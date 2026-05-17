import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { allParameters } from '../data/personas.js';
import { chat } from '../lib/api.js';

const STORAGE_KEY = 'ldm_sessions';

function initialParameterScores() {
  const out = {};
  for (const k of allParameters) out[k] = 0;
  return out;
}

function defaultState() {
  return {
    sessions: [],
    currentSessionId: null,
    parameterScores: initialParameterScores(),
  };
}

function newSessionLocalId() {
  return `local_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [state, setState] = useState(() => {
    if (typeof window === 'undefined') return defaultState();
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (!stored) return defaultState();
      const parsed = JSON.parse(stored);
      return {
        ...defaultState(),
        ...parsed,
        parameterScores: {
          ...initialParameterScores(),
          ...(parsed.parameterScores || {}),
        },
      };
    } catch {
      return defaultState();
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* ignore */
    }
  }, [state]);

  const [pending, setPending] = useState(false);

  const createSession = useCallback(() => {
    const id = newSessionLocalId();
    setState((prev) => ({
      ...prev,
      currentSessionId: id,
      sessions: [
        {
          id,
          title: 'New scenario',
          createdAt: Date.now(),
          updatedAt: Date.now(),
          messages: [],
        },
        ...prev.sessions,
      ],
    }));
    return id;
  }, []);

  const switchSession = useCallback((id) => {
    setState((prev) => ({ ...prev, currentSessionId: id }));
  }, []);

  const deleteSession = useCallback((id) => {
    setState((prev) => {
      const remaining = prev.sessions.filter((s) => s.id !== id);
      const nextCurrent =
        prev.currentSessionId === id
          ? remaining[0]?.id || null
          : prev.currentSessionId;
      return { ...prev, sessions: remaining, currentSessionId: nextCurrent };
    });
  }, []);

  const sendMessage = useCallback(
    async (text) => {
      const trimmed = (text || '').trim();
      if (!trimmed || pending) return;

      // Resolve which session this message belongs to. Create one lazily if
      // there is no current session yet.
      let sessionLocalId = state.currentSessionId;
      let isNewSession = false;
      if (!sessionLocalId) {
        sessionLocalId = newSessionLocalId();
        isNewSession = true;
      }

      // Snapshot the history BEFORE the user turn so we send the backend the
      // same view the user is replying to.
      let history = [];
      const existing = state.sessions.find((s) => s.id === sessionLocalId);
      if (existing) history = existing.messages;

      const userTurn = { role: 'user', content: trimmed, timestamp: Date.now() };

      setState((prev) => {
        if (isNewSession) {
          return {
            ...prev,
            currentSessionId: sessionLocalId,
            sessions: [
              {
                id: sessionLocalId,
                title: 'New scenario',
                createdAt: Date.now(),
                updatedAt: Date.now(),
                messages: [userTurn],
              },
              ...prev.sessions,
            ],
          };
        }
        return {
          ...prev,
          sessions: prev.sessions.map((s) =>
            s.id === sessionLocalId
              ? { ...s, messages: [...s.messages, userTurn], updatedAt: Date.now() }
              : s
          ),
        };
      });

      setPending(true);
      try {
        const res = await chat({
          sessionId: existing?.serverId || null,
          message: trimmed,
          history,
        });

        setState((prev) => {
          const nextScores = { ...prev.parameterScores };
          for (const [k, v] of Object.entries(res.parameterDeltas || {})) {
            nextScores[k] = (nextScores[k] || 0) + v;
          }
          const personaTurns = (res.personaResponses || []).map((r) => ({
            role: 'persona',
            personaId: r.personaId,
            content: r.message,
            timestamp: Date.now(),
          }));
          return {
            ...prev,
            parameterScores: nextScores,
            sessions: prev.sessions.map((s) => {
              if (s.id !== sessionLocalId) return s;
              const nextTitle =
                res.sessionTitle && s.title === 'New scenario'
                  ? res.sessionTitle
                  : s.title;
              return {
                ...s,
                serverId: s.serverId || res.sessionId,
                title: nextTitle,
                situationBrief: res.situationBrief || s.situationBrief,
                updatedAt: Date.now(),
                messages: [...s.messages, ...personaTurns],
              };
            }),
          };
        });
      } catch (err) {
        console.error('[chat] failed', err);
        const detail = err?.message || '알 수 없는 오류';
        setState((prev) => ({
          ...prev,
          sessions: prev.sessions.map((s) =>
            s.id === sessionLocalId
              ? {
                  ...s,
                  messages: [
                    ...s.messages,
                    {
                      role: 'system',
                      content: `백엔드 연결 실패: ${detail}`,
                      timestamp: Date.now(),
                    },
                  ],
                }
              : s
          ),
        }));
        throw err;
      } finally {
        setPending(false);
      }
    },
    [pending, state.currentSessionId, state.sessions]
  );

  const resetAll = useCallback(() => {
    setState(defaultState());
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  }, []);

  const currentSession = useMemo(
    () =>
      state.sessions.find((s) => s.id === state.currentSessionId) || null,
    [state.sessions, state.currentSessionId]
  );

  const value = useMemo(
    () => ({
      ...state,
      currentSession,
      pending,
      createSession,
      switchSession,
      deleteSession,
      sendMessage,
      resetAll,
    }),
    [
      state,
      currentSession,
      pending,
      createSession,
      switchSession,
      deleteSession,
      sendMessage,
      resetAll,
    ]
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSessions() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSessions must be used within SessionProvider');
  return ctx;
}

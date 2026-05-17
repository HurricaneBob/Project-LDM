import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Plus } from 'lucide-react';
import PersonaPortrait from '../components/PersonaPortrait.jsx';
import { useSessions } from '../context/SessionContext.jsx';
import { personas } from '../data/personas.js';

const PERSONAS_BY_ID = Object.fromEntries(personas.map((p) => [p.id, p]));

function formatDate(ts) {
  const d = new Date(ts);
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function previewText(messages) {
  const first = messages.find((m) => m.role === 'user');
  return first?.content || 'No message yet';
}

function uniquePersonas(messages) {
  const seen = new Set();
  for (const m of messages) {
    if (m.role === 'persona' && m.personaId) seen.add(m.personaId);
  }
  return [...seen].map((id) => PERSONAS_BY_ID[id]).filter(Boolean);
}

export default function History() {
  const navigate = useNavigate();
  const { sessions, switchSession, createSession } = useSessions();

  const sorted = useMemo(
    () => [...sessions].sort((a, b) => b.updatedAt - a.updatedAt),
    [sessions]
  );

  const open = (id) => {
    switchSession(id);
    navigate('/');
  };

  const startNew = () => {
    const id = createSession();
    switchSession(id);
    navigate('/');
  };

  return (
    <main className="flex-1 px-6 md:px-10 py-10 overflow-y-auto">
      <header className="max-w-5xl mx-auto mb-8 flex items-end justify-between gap-4">
        <div>
          <span className="text-xs font-medium uppercase tracking-[0.25em] text-primary">
            History
          </span>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight mt-1">
            Your scenarios
          </h1>
          <p className="text-sm text-text-secondary mt-2">
            Every conversation you&rsquo;ve had with the team.
          </p>
        </div>
        <button
          type="button"
          onClick={startNew}
          className="
            inline-flex items-center gap-2 rounded-full px-4 py-2.5
            text-sm font-medium text-white
            bg-primary glow-primary hover:bg-primary-hover hover:glow-primary-hover
            transition-all
          "
        >
          <Plus size={16} /> New scenario
        </button>
      </header>

      {sorted.length === 0 ? (
        <div className="max-w-5xl mx-auto rounded-lg border border-border bg-surface p-10 text-center">
          <p className="text-text-secondary">
            No scenarios yet. Start one to see it here.
          </p>
        </div>
      ) : (
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sorted.map((s) => {
            const involved = uniquePersonas(s.messages);
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => open(s.id)}
                className="
                  text-left rounded-lg border border-border bg-surface
                  hover:border-primary hover:bg-surface-hi transition-all
                  p-5 flex flex-col gap-3 animate-fade-in
                "
              >
                <div className="flex items-start justify-between gap-3">
                  <h2 className="font-semibold tracking-tight line-clamp-2 flex-1">
                    {s.title}
                  </h2>
                  <span className="text-[10px] text-text-muted tabular-nums shrink-0">
                    {formatDate(s.updatedAt)}
                  </span>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed line-clamp-3 min-h-[3.6rem]">
                  {previewText(s.messages)}
                </p>
                <div className="flex items-center justify-between pt-2 border-t border-divider">
                  <div className="flex items-center gap-1.5 text-xs text-text-muted">
                    <MessageSquare size={12} />
                    {s.messages.length}
                  </div>
                  <div className="flex -space-x-2">
                    {involved.length === 0 ? (
                      <span className="text-[10px] text-text-muted">no replies yet</span>
                    ) : (
                      involved.map((p) => (
                        <div key={p.id} className="ring-2 ring-surface rounded-full">
                          <PersonaPortrait persona={p} size="sm" showLabel={false} />
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </main>
  );
}

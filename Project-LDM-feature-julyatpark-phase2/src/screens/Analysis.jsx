import { useEffect, useMemo, useState } from 'react';
import { MessageSquare, Users } from 'lucide-react';
import PersonaPortrait from '../components/PersonaPortrait.jsx';
import { useSessions } from '../context/SessionContext.jsx';
import { fetchFinalEvaluation } from '../lib/api.js';
import { personas, allParameters } from '../data/personas.js';

const PERSONAS_BY_ID = Object.fromEntries(personas.map((p) => [p.id, p]));

function leadershipTypeFromScores(parameterScores) {
  let best = null;
  let bestScore = -1;
  for (const p of personas) {
    let s = 0;
    for (const param of p.evaluates) s += parameterScores[param] || 0;
    if (s > bestScore) {
      bestScore = s;
      best = p;
    }
  }
  return { persona: best, score: bestScore };
}

function mostActivePersona(sessions) {
  const counts = {};
  for (const s of sessions) {
    for (const m of s.messages) {
      if (m.role === 'persona' && m.personaId) {
        counts[m.personaId] = (counts[m.personaId] || 0) + 1;
      }
    }
  }
  let topId = null;
  let topN = 0;
  for (const [id, n] of Object.entries(counts)) {
    if (n > topN) {
      topN = n;
      topId = id;
    }
  }
  return { persona: topId ? PERSONAS_BY_ID[topId] : null, count: topN };
}

export default function Analysis() {
  const { sessions, currentSession, parameterScores } = useSessions();
  const [backendEval, setBackendEval] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalError, setEvalError] = useState(null);

  const serverId = currentSession?.serverId;

  useEffect(() => {
    if (!serverId) {
      setBackendEval(null);
      setEvalError(null);
      return;
    }
    let cancelled = false;
    setEvalLoading(true);
    setEvalError(null);
    fetchFinalEvaluation(serverId)
      .then((data) => {
        if (!cancelled) setBackendEval(data?.evaluation || null);
      })
      .catch((err) => {
        if (!cancelled) setEvalError(err.message);
      })
      .finally(() => {
        if (!cancelled) setEvalLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [serverId]);

  const totalMessages = useMemo(
    () => sessions.reduce((acc, s) => acc + s.messages.length, 0),
    [sessions]
  );

  const { persona: leadershipType, score: leadershipScore } = useMemo(
    () => leadershipTypeFromScores(parameterScores),
    [parameterScores]
  );

  const { persona: topActive, count: topActiveCount } = useMemo(
    () => mostActivePersona(sessions),
    [sessions]
  );

  const sortedParams = useMemo(() => {
    const rows = allParameters.map((p) => ({ name: p, score: parameterScores[p] || 0 }));
    rows.sort((a, b) => b.score - a.score);
    return rows;
  }, [parameterScores]);

  const max = Math.max(1, ...sortedParams.map((r) => r.score));
  const empty = leadershipScore <= 0;

  const holisticText =
    backendEval?.leadership_analysis ||
    backendEval?.holistic_results?.parameter_deltas_analysis ||
    null;

  return (
    <main className="flex-1 px-6 md:px-10 py-10 overflow-y-auto">
      <header className="max-w-5xl mx-auto mb-8">
        <span className="text-xs font-medium uppercase tracking-[0.25em] text-primary">
          Analysis
        </span>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight mt-1">
          Your leadership signal
        </h1>
        <p className="text-sm text-text-secondary mt-2 max-w-xl">
          Accumulated across every scenario you&rsquo;ve run. Updates each time
          the team responds.
        </p>
      </header>

      {empty ? (
        <div className="max-w-5xl mx-auto rounded-lg border border-border bg-surface p-10 text-center">
          <p className="text-text-secondary">
            Run at least one scenario to see your signal here.
          </p>
        </div>
      ) : (
        <div className="max-w-5xl mx-auto flex flex-col gap-6">
          {serverId && (
            <section className="rounded-2xl border border-border bg-surface p-6">
              <p className="text-[10px] uppercase tracking-[0.25em] text-text-muted mb-2">
                Holistic evaluation
              </p>
              {evalLoading && (
                <p className="text-sm text-text-secondary">Loading from server…</p>
              )}
              {evalError && (
                <p className="text-sm text-text-secondary">
                  Could not load server evaluation: {evalError}
                </p>
              )}
              {!evalLoading && holisticText && (
                <p className="text-sm text-text leading-relaxed">{holisticText}</p>
              )}
              {!evalLoading && !holisticText && !evalError && (
                <p className="text-sm text-text-secondary">
                  Continue the scenario to build enough data for a holistic summary.
                </p>
              )}
              {backendEval?.strengths?.length > 0 && (
                <ul className="mt-3 text-sm text-text-secondary list-disc pl-5">
                  {backendEval.strengths.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              )}
            </section>
          )}

          <section
            className="rounded-2xl border border-border bg-surface p-6 md:p-8 flex items-center gap-6 flex-wrap"
            style={{
              backgroundImage:
                'radial-gradient(circle at 0% 0%, rgba(168, 85, 247, 0.08), transparent 60%)',
            }}
          >
            {leadershipType && (
              <PersonaPortrait persona={leadershipType} speaking size="lg" showLabel={false} />
            )}
            <div className="flex-1 min-w-[200px]">
              <p className="text-[10px] uppercase tracking-[0.25em] text-text-muted">
                Your leadership type
              </p>
              <h2
                className="text-3xl md:text-4xl font-bold tracking-tight mt-1"
                style={{ color: `var(${leadershipType.colorVar})` }}
              >
                {leadershipType.name}
              </h2>
              <p className="text-sm text-text-secondary mt-2 max-w-md">
                {leadershipType.description}
              </p>
              <p className="text-xs text-text-muted mt-3">
                Strongest dimensions: {leadershipType.evaluates.slice(0, 3).join(', ')}
              </p>
            </div>
          </section>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard label="Scenarios" value={sessions.length} icon={<Users size={16} />} />
            <StatCard
              label="Total messages"
              value={totalMessages}
              icon={<MessageSquare size={16} />}
            />
            <StatCard
              label="Most active voice"
              value={topActive ? topActive.name : '—'}
              valueColor={topActive ? `var(${topActive.colorVar})` : undefined}
              sub={topActive ? `${topActiveCount} replies` : ''}
            />
          </section>

          <section className="rounded-2xl border border-border bg-surface p-6">
            <p className="text-[10px] uppercase tracking-[0.25em] text-text-muted mb-4">
              Parameter scores
            </p>
            <div className="flex flex-col gap-2.5">
              {sortedParams.map((r) => (
                <div key={r.name} className="flex items-center gap-3">
                  <span className="text-sm text-text flex-1 min-w-0 truncate">
                    {r.name}
                  </span>
                  <div className="h-1.5 w-56 bg-surface-hi rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${(r.score / max) * 100}%`,
                        background:
                          'linear-gradient(90deg, var(--color-primary), var(--color-primary-hover))',
                        boxShadow: r.score > 0 ? '0 0 12px rgba(168,85,247,0.4)' : 'none',
                      }}
                    />
                  </div>
                  <span className="text-sm text-text-muted tabular-nums w-8 text-right">
                    {r.score}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

function StatCard({ label, value, icon, valueColor, sub }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-text-muted text-[10px] uppercase tracking-[0.2em]">
        {icon} <span>{label}</span>
      </div>
      <p
        className="text-2xl font-bold tracking-tight"
        style={valueColor ? { color: valueColor } : undefined}
      >
        {value}
      </p>
      {sub && <p className="text-xs text-text-muted">{sub}</p>}
    </div>
  );
}

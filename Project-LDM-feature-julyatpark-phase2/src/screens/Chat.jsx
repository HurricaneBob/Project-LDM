import { useEffect, useMemo, useRef, useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';
import PersonaAvatar from '../components/PersonaAvatar.jsx';
import PersonaCharacter from '../components/PersonaCharacter.jsx';
import VoiceOrb from '../components/VoiceOrb.jsx';
import AiResponseBackground from '../components/AiResponseBackground.jsx';
import { useSessions } from '../context/SessionContext.jsx';
import { personas } from '../data/personas.js';

const PERSONAS_BY_ID = Object.fromEntries(personas.map((p) => [p.id, p]));

function lastPersonaTurn(messages) {
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === 'persona') return messages[i];
  }
  return null;
}

export default function Chat() {
  const { currentSession, pending, sendMessage, createSession } = useSessions();

  const messages = currentSession?.messages || [];
  const hasMessages = messages.length > 0;

  // inputMode: 'voice' (default, idle) | 'text'
  const [inputMode, setInputMode] = useState('voice');
  const [draft, setDraft] = useState('');
  const [listening, setListening] = useState(false);
  const inputRef = useRef(null);
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);

  // Halftone background tracks pending exactly. The fade-out itself takes
  // 800ms (CSS) so removing visibility immediately still feels gentle.
  const [bgVisible, setBgVisible] = useState(false);
  useEffect(() => {
    setBgVisible(pending);
  }, [pending]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages.length, pending]);

  useEffect(() => {
    if (inputMode === 'text') {
      inputRef.current?.focus();
    }
  }, [inputMode]);

  const speaker = useMemo(() => {
    if (!hasMessages) return null;
    const last = lastPersonaTurn(messages);
    return last ? PERSONAS_BY_ID[last.personaId] : null;
  }, [messages, hasMessages]);

  const lastPersonaIdx = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'persona') return i;
    }
    return -1;
  }, [messages]);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || pending) return;
    setDraft('');
    try {
      if (!currentSession) createSession();
      await sendMessage(text);
    } catch (err) {
      // SessionContext appends a red system message; restore draft for retry.
      setDraft(text);
      console.error('[Chat] sendMessage failed', err);
    }
  };

  const handleMicToggle = () => {
    // Phase 1: visual placeholder. Click toggles "listening" UI only.
    setListening((v) => !v);
  };

  // ─── Idle state ───────────────────────────────────────────────────────────
  if (!hasMessages && inputMode === 'voice') {
    return (
      <main className="flex-1 flex flex-col px-6 md:px-10 py-10 relative">
        <div className="flex-1 flex flex-col items-center justify-center gap-12">
          <div className="dot-pattern h-6 w-32 text-primary opacity-50" aria-hidden />
          <div
            className="
              px-8 py-6 rounded-3xl bg-surface border border-border
              text-2xl md:text-3xl font-medium tracking-tight text-text
              max-w-xl text-center
            "
          >
            Hi. What&rsquo;s Up?
          </div>
          <p className="text-sm text-text-secondary max-w-md text-center">
            Describe a leadership situation you&rsquo;re sitting with. The team
            will respond as if you were leading them.
          </p>
        </div>

        {/* Bottom bar — mic + text toggle */}
        <div className="flex flex-col items-center gap-3">
          {listening && (
            <p className="text-xs uppercase tracking-[0.25em] text-text-secondary">
              Listening…
            </p>
          )}
          <div className="flex items-center justify-center gap-6">
            <button
              type="button"
              onClick={handleMicToggle}
              aria-label={listening ? 'Stop listening' : 'Start voice input'}
              className="transition-transform duration-200 hover:-translate-y-0.5 focus:outline-none"
            >
              <VoiceOrb active={listening} size={listening ? 120 : 32} />
            </button>
            <button
              type="button"
              onClick={() => setInputMode('text')}
              aria-label="Switch to text input"
              className="
                w-12 h-12 rounded-full bg-surface border border-border
                flex items-center justify-center text-text-secondary
                hover:text-text hover:bg-surface-hi transition-colors
              "
            >
              <MessageSquare size={18} />
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ─── Text-input on empty session ──────────────────────────────────────────
  if (!hasMessages && inputMode === 'text') {
    return (
      <main className="flex-1 flex flex-col px-6 md:px-10 py-10">
        <div className="flex-1 flex flex-col items-center justify-center gap-10">
          <div className="dot-pattern h-6 w-32 text-primary opacity-50" aria-hidden />
          <div
            className="
              px-8 py-6 rounded-3xl bg-surface border border-border
              text-2xl md:text-3xl font-medium tracking-tight text-text
              max-w-xl text-center
            "
          >
            Hi. What&rsquo;s Up?
          </div>
          <p className="text-sm text-text-secondary max-w-md text-center">
            Tell the team what&rsquo;s on your mind.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex items-center gap-3 max-w-2xl w-full mx-auto">
          <div className="flex-1 flex items-center gap-2 rounded-full bg-surface border border-border focus-within:border-primary focus-within:focus-ring-primary transition-all px-5 py-3">
            <input
              ref={inputRef}
              type="text"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Describe the situation…"
              className="flex-1 bg-transparent outline-none text-text placeholder:text-text-muted"
              disabled={pending}
            />
            <button
              type="button"
              onClick={() => setInputMode('voice')}
              className="text-text-muted hover:text-text transition-colors"
              aria-label="Switch to voice"
            >
              <VoiceOrb active={false} size={32} />
            </button>
          </div>
          <button
            type="submit"
            disabled={!draft.trim() || pending}
            aria-label="Send"
            className="
              w-12 h-12 shrink-0 rounded-full bg-primary text-white
              flex items-center justify-center glow-primary
              hover:glow-primary-hover hover:bg-primary-hover transition-all
              disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none
            "
          >
            <Send size={18} />
          </button>
        </form>
      </main>
    );
  }

  // ─── Active session ───────────────────────────────────────────────────────
  return (
    <main className="flex-1 min-h-0 flex flex-col">
      {/* Header: session title — stays pinned */}
      <header className="shrink-0 px-6 md:px-10 pt-5 pb-3 border-b border-divider">
        <p className="text-[10px] uppercase tracking-[0.25em] text-text-muted">
          Scenario
        </p>
        <h1 className="text-lg md:text-xl font-semibold tracking-tight truncate">
          {currentSession?.title || 'Untitled scenario'}
        </h1>
        {currentSession?.situationBrief && (
          <p className="text-sm text-text-secondary mt-2 max-w-3xl leading-relaxed">
            {currentSession.situationBrief}
          </p>
        )}
      </header>

      {/* Avatar row — stays pinned. Last speaker glows. */}
      <section className="shrink-0 px-6 md:px-10 py-5 border-b border-divider">
        <div className="flex justify-center gap-6 md:gap-10 flex-wrap">
          {personas.map((p) => (
            <PersonaAvatar
              key={p.id}
              persona={p}
              active={speaker?.id === p.id}
            />
          ))}
        </div>
      </section>

      {/* Conversation — the ONLY scrollable region */}
      <section className="flex-1 min-h-0 px-6 md:px-10 py-6 overflow-hidden relative">
        <AiResponseBackground visible={bgVisible} />
        <div
          ref={scrollRef}
          className="relative z-10 max-w-5xl mx-auto h-full overflow-y-auto pr-1 flex flex-col gap-4"
        >
          {messages.map((m, i) => {
            if (m.role === 'user') {
              return (
                <div key={i} className="flex justify-end animate-fade-in">
                  <div className="max-w-[70%] bg-primary text-white px-4 py-3 rounded-2xl rounded-tr-sm">
                    <p className="text-sm leading-relaxed">{m.content}</p>
                  </div>
                </div>
              );
            }
            if (m.role === 'system') {
              return (
                <div key={i} className="flex justify-center animate-fade-in px-2">
                  <p className="text-sm text-red-500 font-medium text-center max-w-lg leading-relaxed">
                    {m.content}
                  </p>
                </div>
              );
            }
            const p = PERSONAS_BY_ID[m.personaId];
            if (!p) return null;
            const personaColor = `var(${p.colorVar})`;
            const isLastPersona = i === lastPersonaIdx;
            return (
              <div
                key={i}
                className="flex items-end gap-4 animate-fade-in"
              >
                {/* Left slot — character only renders for the latest persona */}
                <div className="w-[220px] shrink-0 hidden md:flex justify-end items-end">
                  {isLastPersona && (
                    <PersonaCharacter key={p.id} persona={p} size={180} />
                  )}
                </div>
                <div
                  className="max-w-[60%] bg-surface border px-4 py-3 rounded-2xl rounded-tl-sm"
                  style={{ borderColor: personaColor }}
                >
                  <p
                    className="text-[10px] font-semibold uppercase tracking-[0.25em] mb-1"
                    style={{ color: personaColor }}
                  >
                    {p.name}
                  </p>
                  <p className="text-sm leading-relaxed text-text">{m.content}</p>
                </div>
              </div>
            );
          })}
          {pending && (
            <div className="flex items-end gap-4 animate-fade-in">
              <div className="w-[220px] shrink-0 hidden md:block" aria-hidden />
              <div className="bg-surface border border-border px-4 py-3 rounded-2xl rounded-tl-sm">
                <span className="text-sm text-text-muted">The team is thinking…</span>
              </div>
            </div>
          )}
          {/* Scroll-to-bottom anchor */}
          <div ref={bottomRef} />
        </div>
      </section>

      {/* Input bar */}
      <footer className="shrink-0 px-6 md:px-10 py-5 border-t border-divider bg-bg">
        <div className="max-w-3xl mx-auto">
          {inputMode === 'text' ? (
            <form onSubmit={handleSubmit} className="flex items-center gap-3">
              <div className="flex-1 flex items-center gap-2 rounded-full bg-surface border border-border focus-within:border-primary focus-within:focus-ring-primary transition-all px-5 py-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Reply to the team…"
                  className="flex-1 bg-transparent outline-none text-text placeholder:text-text-muted"
                  disabled={pending}
                />
                <button
                  type="button"
                  onClick={() => setInputMode('voice')}
                  className="text-text-muted hover:text-text transition-colors"
                  aria-label="Switch to voice"
                >
                  <VoiceOrb active={false} size={32} />
                </button>
              </div>
              <button
                type="submit"
                disabled={!draft.trim() || pending}
                aria-label="Send"
                className="
                  w-12 h-12 shrink-0 rounded-full bg-primary text-white
                  flex items-center justify-center glow-primary
                  hover:glow-primary-hover hover:bg-primary-hover transition-all
                  disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none
                "
              >
                <Send size={18} />
              </button>
            </form>
          ) : (
            <div className="flex flex-col items-center gap-3">
              {listening && (
                <p className="text-xs uppercase tracking-[0.25em] text-text-secondary">
                  Listening…
                </p>
              )}
              <div className="flex items-center justify-center gap-6">
                <button
                  type="button"
                  onClick={handleMicToggle}
                  aria-label={listening ? 'Stop listening' : 'Start voice input'}
                  className="transition-transform duration-200 hover:-translate-y-0.5 focus:outline-none"
                >
                  <VoiceOrb active={listening} size={listening ? 120 : 32} />
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode('text')}
                  aria-label="Switch to text"
                  className="
                    w-12 h-12 rounded-full bg-surface border border-border
                    flex items-center justify-center text-text-secondary
                    hover:text-text hover:bg-surface-hi transition-colors
                  "
                >
                  <MessageSquare size={18} />
                </button>
              </div>
            </div>
          )}
        </div>
      </footer>
    </main>
  );
}

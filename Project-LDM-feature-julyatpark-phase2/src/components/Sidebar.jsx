import { useState } from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Plus,
  PanelLeftClose,
  History as HistoryIcon,
  BarChart3,
  Bug,
  Trash2,
  LogOut,
  User as UserIcon,
} from 'lucide-react';
import { useSessions } from '../context/SessionContext.jsx';
import { useOnboarding } from '../context/OnboardingContext.jsx';

function relativeTime(ts) {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60_000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 7) return `${d}d ago`;
  return new Date(ts).toLocaleDateString();
}

export default function Sidebar({ collapsed = false, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();
  const {
    sessions,
    currentSessionId,
    createSession,
    switchSession,
    deleteSession,
  } = useSessions();
  const { data } = useOnboarding();

  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = () => {
    setUserMenuOpen(false);
    navigate('/onboarding/welcome');
  };

  const handleAddScenario = () => {
    const id = createSession();
    navigate('/');
    // Make sure the new session is the active one even if we were already on /.
    switchSession(id);
  };

  const handleSwitch = (id) => {
    switchSession(id);
    navigate('/');
  };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    deleteSession(id);
  };

  const displayName = data.name?.trim() || 'You';
  const email = data.email?.trim?.() || '';

  return (
    <aside
      className="
        shrink-0 border-r border-divider bg-bg
        h-screen sticky top-0 overflow-hidden
        transition-[width] duration-300 ease-out
      "
      style={{ width: collapsed ? 0 : 288 }}
      aria-hidden={collapsed}
    >
      <div className="w-72 h-full flex flex-col">
        {/* Top: logo + collapse toggle */}
        <div className="px-4 pt-5 pb-3 flex items-center justify-between">
          <Link
            to="/"
            aria-label="LDM home"
            className="inline-flex items-center hover:opacity-80 transition-opacity"
          >
            <img
              src="/images/LDM.svg"
              alt="LDM"
              style={{ height: 28, width: 'auto' }}
              draggable={false}
            />
          </Link>
          <button
            type="button"
            onClick={onToggle}
            className="text-text-muted hover:text-text transition-colors p-1 rounded"
            aria-label="Collapse sidebar"
          >
            <PanelLeftClose size={18} />
          </button>
        </div>

      {/* Add Scenario CTA */}
      <div className="px-4 pb-3">
        <button
          type="button"
          onClick={handleAddScenario}
          className="
            w-full inline-flex items-center justify-center gap-2
            rounded-full px-4 py-3
            text-sm font-medium text-white
            bg-gradient-to-r from-primary to-primary-hover
            glow-primary hover:glow-primary-hover
            transition-all duration-200 hover:-translate-y-0.5
          "
        >
          <Plus size={18} /> Add Scenario
        </button>
      </div>

      {/* Session list */}
      <div className="px-2 flex-1 overflow-y-auto">
        <p className="text-[10px] uppercase tracking-[0.2em] text-text-muted px-3 py-2">
          Scenarios
        </p>
        {sessions.length === 0 ? (
          <p className="text-xs text-text-muted px-3 py-2">
            No scenarios yet. Add one to start.
          </p>
        ) : (
          <ul className="flex flex-col gap-0.5">
            {sessions.map((s) => {
              const isActive =
                s.id === currentSessionId && location.pathname === '/';
              return (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => handleSwitch(s.id)}
                    className={`
                      group w-full text-left flex items-center gap-2
                      px-3 py-2 rounded-md transition-colors
                      ${isActive
                        ? 'bg-surface-hi text-text'
                        : 'text-text-secondary hover:bg-surface hover:text-text'}
                    `}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate">{s.title}</p>
                      <p className="text-[10px] text-text-muted">
                        {relativeTime(s.updatedAt)} · {s.messages.length} msg
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(e, s.id)}
                      className="opacity-0 group-hover:opacity-100 text-text-muted hover:text-error transition"
                      aria-label="Delete scenario"
                    >
                      <Trash2 size={14} />
                    </button>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Nav menu */}
      <div className="px-2 py-3 border-t border-divider">
        <NavLink
          to="/history"
          className={({ isActive }) => `
            flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors
            ${isActive
              ? 'bg-surface-hi text-text'
              : 'text-text-secondary hover:bg-surface hover:text-text'}
          `}
        >
          <HistoryIcon size={16} /> History
        </NavLink>
        <NavLink
          to="/analysis"
          className={({ isActive }) => `
            flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors
            ${isActive
              ? 'bg-surface-hi text-text'
              : 'text-text-secondary hover:bg-surface hover:text-text'}
          `}
        >
          <BarChart3 size={16} /> Analysis
        </NavLink>
      </div>

      {/* Footer: bug + user chip */}
      <div className="p-3 border-t border-divider flex items-center gap-2">
        <button
          type="button"
          className="text-text-muted hover:text-text p-2 rounded transition-colors"
          aria-label="Report a bug"
          title="Report a bug (coming soon)"
        >
          <Bug size={16} />
        </button>

        <div className="relative flex-1">
          <button
            type="button"
            onClick={() => setUserMenuOpen((v) => !v)}
            className="
              w-full flex items-center gap-2 px-2 py-2 rounded-md
              hover:bg-surface transition-colors text-left
            "
          >
            <div className="w-7 h-7 rounded-full bg-surface-hi flex items-center justify-center shrink-0">
              <UserIcon size={14} className="text-text-secondary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{displayName}</p>
              {email && (
                <p className="text-[10px] text-text-muted truncate">{email}</p>
              )}
            </div>
          </button>
          {userMenuOpen && (
            <div
              className="absolute bottom-full left-0 right-0 mb-2 bg-surface border border-border rounded-md shadow-lg animate-fade-in"
              role="menu"
            >
              <button
                type="button"
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text hover:bg-surface-hi rounded-md transition-colors"
              >
                <LogOut size={14} /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
      </div>
    </aside>
  );
}

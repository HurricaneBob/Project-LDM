import { Check } from 'lucide-react';

/**
 * PillButton — used in option groups (role, personality questions, etc.)
 *
 *   - mode="single": violet active state, no icon
 *   - mode="multi":  white active state with check icon (signals multi-select)
 */
export default function PillButton({
  active = false,
  mode = 'single',
  onClick,
  children,
  className = '',
}) {
  const base =
    'inline-flex items-center gap-1.5 rounded-full px-5 py-2.5 text-sm font-medium transition-all duration-150 select-none';

  const inactive =
    'bg-surface border border-border text-text-secondary hover:bg-surface-hi hover:border-text-muted';

  const activeSingle =
    'bg-primary border border-primary text-white glow-primary';

  const activeMulti =
    'bg-white border border-white text-bg';

  const activeClass = active
    ? mode === 'multi'
      ? activeMulti
      : activeSingle
    : inactive;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${base} ${activeClass} ${className}`}
    >
      {active && mode === 'multi' && <Check size={14} strokeWidth={3} />}
      <span>{children}</span>
    </button>
  );
}

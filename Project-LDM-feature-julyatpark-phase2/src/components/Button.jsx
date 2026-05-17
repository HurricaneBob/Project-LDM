/**
 * Button component with a 4-tier hierarchy:
 *   - hero:    large white pill + strong glow (max emphasis, 1 per page)
 *   - primary: violet pill + subtle glow (standard CTA)
 *   - secondary: white pill (rare highlight, no glow)
 *   - ghost:   transparent + subtle border (back, skip, cancel)
 *
 * All variants are pill-shaped via `rounded-full`.
 */

const sizeClasses = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-base',
  lg: 'px-7 py-3.5 text-base',
};

const variantClasses = {
  hero: [
    'bg-white text-bg font-semibold',
    'glow-white hover:glow-white-hover',
    'hover:-translate-y-0.5',
  ].join(' '),
  primary: [
    'bg-primary text-white font-medium',
    'glow-primary hover:glow-primary-hover',
    'hover:bg-primary-hover',
  ].join(' '),
  secondary: [
    'bg-white text-bg font-medium',
    'hover:bg-secondary-hover',
  ].join(' '),
  ghost: [
    'bg-transparent border border-border text-text',
    'hover:bg-surface-hi hover:border-text-secondary',
  ].join(' '),
};

export default function Button({
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  className = '',
  onClick,
  children,
  ...rest
}) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-full transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0 disabled:shadow-none';
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${base} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

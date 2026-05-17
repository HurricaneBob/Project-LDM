import { useState } from 'react';

const sizeMap = {
  sm: { box: 'w-12 h-12', label: 'text-[10px]', initial: 'text-lg' },
  md: { box: 'w-20 h-20', label: 'text-xs', initial: 'text-2xl' },
  lg: { box: 'w-28 h-28', label: 'text-sm', initial: 'text-4xl' },
};

export default function PersonaPortrait({
  persona,
  speaking = false,
  size = 'md',
  showLabel = true,
}) {
  const s = sizeMap[size] || sizeMap.md;
  const [imgError, setImgError] = useState(false);
  const personaColor = `var(${persona.colorVar})`;

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`relative ${s.box} rounded-full overflow-hidden transition-all duration-500
          ${speaking ? 'scale-105' : 'scale-100 opacity-60'}`}
        style={{
          boxShadow: speaking
            ? `0 0 0 2px ${personaColor}, 0 0 28px ${personaColor}, 0 0 56px ${personaColor}`
            : `0 0 0 1px var(--color-border)`,
        }}
        aria-label={persona.name}
      >
        {!imgError ? (
          <img
            src={persona.image}
            alt={persona.name}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center font-bold"
            style={{
              background: `radial-gradient(circle at 50% 35%, ${personaColor} 0%, transparent 70%), var(--color-surface-hi)`,
              color: personaColor,
            }}
          >
            <span className={`${s.initial} drop-shadow`}>
              {persona.name.replace(/^The\s+/, '').charAt(0)}
            </span>
          </div>
        )}
        {speaking && (
          <span
            className="absolute inset-0 rounded-full animate-glow-pulse pointer-events-none"
            style={{ boxShadow: `inset 0 0 24px ${personaColor}` }}
            aria-hidden
          />
        )}
      </div>

      {showLabel && (
        <span
          className={`${s.label} font-medium tracking-tight transition-colors`}
          style={{ color: speaking ? personaColor : 'var(--color-text-secondary)' }}
        >
          {persona.name.replace(/^The\s+/, '')}
        </span>
      )}
    </div>
  );
}

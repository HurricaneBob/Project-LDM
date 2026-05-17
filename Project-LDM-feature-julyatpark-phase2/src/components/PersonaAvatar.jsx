import { useState } from 'react';

// Circular avatar used in the top row of the Chat screen.
//
// Props:
//   persona — persona object (must have id, name, colorVar)
//   active  — true when this persona is the most recent speaker (drives glow)

export default function PersonaAvatar({ persona, active = false }) {
  const [imgError, setImgError] = useState(false);
  const personaColor = `var(${persona.colorVar})`;
  const shortName = persona.name.replace(/^The\s+/, '');

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="relative w-20 h-20 rounded-full overflow-hidden transition-all duration-500"
        style={{
          background: `radial-gradient(circle at 50% 35%, ${personaColor}, transparent 75%), var(--color-surface)`,
          boxShadow: active
            ? `0 0 0 2px ${personaColor}, 0 0 24px ${personaColor}, 0 0 48px ${personaColor}`
            : `0 0 0 1px var(--color-border)`,
          opacity: active ? 1 : 0.6,
        }}
        aria-label={persona.name}
      >
        {!imgError ? (
          <img
            src={`/personas/${persona.id}-avatar.png`}
            alt={persona.name}
            className="w-full h-full object-contain"
            onError={() => setImgError(true)}
            draggable={false}
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center font-bold text-2xl"
            style={{ color: personaColor }}
          >
            {shortName.charAt(0)}
          </div>
        )}
      </div>
      <span
        className="text-[10px] uppercase tracking-[0.2em] font-semibold transition-colors"
        style={{ color: active ? personaColor : 'var(--color-text-secondary)' }}
      >
        {shortName}
      </span>
    </div>
  );
}

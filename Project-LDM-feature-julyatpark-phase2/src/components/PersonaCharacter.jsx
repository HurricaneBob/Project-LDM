import { useState } from 'react';

// Full-body chibi PNG rendered next to the last persona message.
// Intentionally has no box, border, or background — the PNG's own
// transparency is the silhouette.
//
// Props:
//   persona — persona object
//   size    — px width (default 280). Height auto from PNG aspect.

export default function PersonaCharacter({ persona, size = 180 }) {
  const [imgError, setImgError] = useState(false);
  const personaColor = `var(${persona.colorVar})`;
  const shortName = persona.name.replace(/^The\s+/, '');
  // Per-persona scale normalizes apparent figure height across PNGs whose
  // natural aspect ratios differ. See `characterScale` in personas.js.
  const scaledSize = size * (persona.characterScale ?? 1);

  return (
    <div
      className="animate-fade-in pointer-events-none select-none flex items-end justify-center"
      style={{ width: size, height: size * 1.626 }}
      aria-hidden
    >
      {/* Inner wrapper carries the ambient float — keeps outer fade-in transform
          and inner translate separated so they don't fight. */}
      <div className="persona-character-float flex items-end justify-center w-full h-full">
        {!imgError ? (
          <img
            src={`/personas/${persona.id}-character.png`}
            alt={persona.name}
            onError={() => setImgError(true)}
            draggable={false}
            style={{
              width: scaledSize,
              height: 'auto',
              objectFit: 'contain',
              display: 'block',
            }}
          />
        ) : (
          // Placeholder: a soft color disc + persona name. No frame, no border.
          <div
            className="flex flex-col items-center justify-end gap-3"
            style={{ width: '100%' }}
          >
            <div
              className="rounded-full"
              style={{
                width: size * 0.7,
                height: size * 0.7,
                background: `radial-gradient(circle at 50% 40%, ${personaColor}, transparent 75%)`,
                filter: 'blur(1px)',
              }}
            />
            <span
              className="text-sm font-semibold tracking-[0.2em] uppercase"
              style={{ color: personaColor }}
            >
              {shortName}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import Lottie from 'lottie-react';
import { Mic } from 'lucide-react';

// VoiceOrb: morphs between a static Mic icon (idle) and a Lottie animation
// (listening). Cross-fades over 200ms.
//
// Props:
//   active — true while "listening"
//   size   — square px size (default 48)

const ANIMATION_URL = '/animations/voice-orb.json';

// Module-level cache so the JSON is fetched at most once across all instances.
let animationCache = null;
let inflight = null;
function getAnimationData() {
  if (animationCache) return Promise.resolve(animationCache);
  if (!inflight) {
    inflight = fetch(ANIMATION_URL)
      .then((r) => r.json())
      .then((d) => {
        animationCache = d;
        return d;
      })
      .catch((err) => {
        console.error('[VoiceOrb] failed to load animation', err);
        return null;
      });
  }
  return inflight;
}

export default function VoiceOrb({ active = false, size = 32 }) {
  const [animationData, setAnimationData] = useState(animationCache);

  useEffect(() => {
    if (!animationData) {
      let cancelled = false;
      getAnimationData().then((d) => {
        if (!cancelled) setAnimationData(d);
      });
      return () => {
        cancelled = true;
      };
    }
  }, [animationData]);

  return (
    <div
      className="relative"
      style={{
        width: size,
        height: size,
        transition: 'width 200ms ease-out, height 200ms ease-out',
      }}
      aria-hidden
    >
      {/* Mic icon layer (visible when idle) */}
      <div
        className="absolute inset-0 flex items-center justify-center text-text"
        style={{
          opacity: active ? 0 : 1,
          transition: 'opacity 200ms ease-out',
        }}
      >
        <Mic size={Math.round(size * 0.55)} />
      </div>

      {/* Lottie layer (visible when listening) */}
      <div
        className="absolute inset-0"
        style={{
          opacity: active && animationData ? 1 : 0,
          transition: 'opacity 200ms ease-out',
        }}
      >
        {animationData && (
          <Lottie
            animationData={animationData}
            loop
            autoplay={active}
            style={{ width: '100%', height: '100%' }}
          />
        )}
      </div>
    </div>
  );
}

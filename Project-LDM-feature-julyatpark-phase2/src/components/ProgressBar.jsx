/**
 * Onboarding progress bar — segmented, with active gradient.
 * Pass `current` (1-indexed) and `total`.
 */
export default function ProgressBar({ current, total }) {
  return (
    <div
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={1}
      aria-valuemax={total}
      className="flex w-full gap-2"
    >
      {Array.from({ length: total }).map((_, i) => {
        const stepIndex = i + 1;
        const isActive = stepIndex <= current;
        return (
          <div
            key={i}
            className={`
              h-1 flex-1 rounded-full transition-all duration-500
              ${isActive ? 'bg-primary glow-primary' : 'bg-surface-hi'}
            `}
          />
        );
      })}
    </div>
  );
}

import ProgressBar from './ProgressBar.jsx';

/**
 * Shared layout chrome for onboarding steps:
 *   - top bar with logo + progress
 *   - centered content
 *   - sticky-feel footer for nav buttons
 *
 * Pass `step` (1..N) and `totalSteps` (defaults to 4).
 */
export default function OnboardingLayout({
  step,
  totalSteps = 4,
  children,
  footer,
}) {
  return (
    <main className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="px-6 md:px-10 pt-6 pb-4 flex items-center gap-6">
        <div className="shrink-0">
          <img
            src="/images/LDM.svg"
            alt="LDM"
            style={{ height: 32, width: 'auto' }}
            draggable={false}
          />
        </div>
        <div className="flex-1 max-w-2xl">
          <ProgressBar current={step} total={totalSteps} />
        </div>
        <span className="text-xs text-text-muted tabular-nums shrink-0">
          {step} / {totalSteps}
        </span>
      </header>

      {/* Content */}
      <section className="flex-1 flex items-center justify-center px-6 py-8">
        <div className="w-full max-w-3xl animate-fade-in">{children}</div>
      </section>

      {/* Footer */}
      {footer && (
        <footer className="px-6 md:px-10 py-6 border-t border-divider">
          <div className="max-w-3xl mx-auto flex items-center justify-between gap-4">
            {footer}
          </div>
        </footer>
      )}
    </main>
  );
}

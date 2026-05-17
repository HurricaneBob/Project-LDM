import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import OnboardingLayout from '../../components/OnboardingLayout.jsx';
import Button from '../../components/Button.jsx';

export default function Welcome() {
  const navigate = useNavigate();
  return (
    <OnboardingLayout
      step={1}
      footer={
        <>
          <span className="text-xs text-text-muted">Step 1 of 5</span>
          <Button
            variant="hero"
            size="lg"
            onClick={() => navigate('/onboarding/profile')}
          >
            Get started <ArrowRight size={18} />
          </Button>
        </>
      }
    >
      <div className="flex flex-col items-center text-center gap-8 py-12">
        {/* Decorative dot strip */}
        <div
          className="dot-pattern h-6 w-32 text-primary opacity-60"
          aria-hidden
        />

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight leading-[1.05] max-w-3xl">
          Become the leader your team needs.
        </h1>

        <p className="text-base md:text-lg text-text-secondary max-w-xl leading-relaxed">
          Step into five scenarios. Meet five mentor personas. Learn when to
          push, when to listen, and when to bridge.
        </p>
      </div>
    </OnboardingLayout>
  );
}

import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import OnboardingLayout from '../../components/OnboardingLayout.jsx';
import Button from '../../components/Button.jsx';
import { useOnboarding } from '../../context/OnboardingContext.jsx';

export default function Ready() {
  const navigate = useNavigate();
  const { data } = useOnboarding();
  const displayName = data.name?.trim() || 'leader';

  const handleStart = () => {
    navigate('/');
  };

  return (
    <OnboardingLayout
      step={4}
      footer={
        <>
          <Button
            variant="ghost"
            onClick={() => navigate('/onboarding/about-you')}
          >
            <ArrowLeft size={18} /> Back
          </Button>
          <Button variant="hero" size="lg" onClick={handleStart}>
            Meet your team <Sparkles size={18} />
          </Button>
        </>
      }
    >
      <div className="flex flex-col items-center text-center gap-8 py-16">
        <div
          className="dot-pattern h-6 w-32 text-primary opacity-60"
          aria-hidden
        />

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight leading-[1.05] max-w-3xl">
          Ready when you are, {displayName}.
        </h1>

        <p className="text-base md:text-lg text-text-secondary max-w-xl leading-relaxed">
          Bring any leadership situation — a stuck team, a hard call, a
          conversation you&rsquo;re dreading. Your AI team will respond as if
          you were leading them.
        </p>
      </div>
    </OnboardingLayout>
  );
}

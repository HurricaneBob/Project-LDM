import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import OnboardingLayout from '../../components/OnboardingLayout.jsx';
import Button from '../../components/Button.jsx';
import Input from '../../components/Input.jsx';
import PillButton from '../../components/PillButton.jsx';
import { useOnboarding } from '../../context/OnboardingContext.jsx';
import { roleOptions } from '../../data/personas.js';

export default function Profile() {
  const navigate = useNavigate();
  const { data, update } = useOnboarding();

  const canContinue = data.name.trim().length > 0 && data.role.length > 0;

  return (
    <OnboardingLayout
      step={2}
      footer={
        <>
          <Button
            variant="ghost"
            onClick={() => navigate('/onboarding/welcome')}
          >
            <ArrowLeft size={18} /> Back
          </Button>
          <Button
            variant="primary"
            disabled={!canContinue}
            onClick={() => navigate('/onboarding/about-you')}
          >
            Continue <ArrowRight size={18} />
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-8 max-w-xl mx-auto py-4">
        <header className="flex flex-col gap-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-primary">
            Profile
          </span>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            Tell us about you.
          </h1>
          <p className="text-sm text-text-secondary">
            We&rsquo;ll personalize your journey.
          </p>
        </header>

        <div className="flex flex-col gap-6">
          <Input
            label="Your name"
            name="name"
            placeholder="e.g. Kent"
            value={data.name}
            onChange={(e) => update({ name: e.target.value })}
            autoFocus
          />

          <div className="flex flex-col gap-3">
            <label className="text-sm font-medium text-text-secondary tracking-wide">
              What&rsquo;s your role?
            </label>
            <div className="flex flex-wrap gap-2">
              {roleOptions.map((opt) => (
                <PillButton
                  key={opt}
                  active={data.role === opt}
                  onClick={() => update({ role: opt })}
                >
                  {opt}
                </PillButton>
              ))}
            </div>
          </div>
        </div>
      </div>
    </OnboardingLayout>
  );
}

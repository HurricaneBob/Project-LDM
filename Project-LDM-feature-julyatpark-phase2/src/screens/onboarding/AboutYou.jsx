import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import OnboardingLayout from '../../components/OnboardingLayout.jsx';
import Button from '../../components/Button.jsx';
import PillButton from '../../components/PillButton.jsx';
import { useOnboarding } from '../../context/OnboardingContext.jsx';
import {
  pressureOptions,
  conflictOptions,
  growthAreaOptions,
} from '../../data/personas.js';

function QuestionCard({ index, label, mode = 'single', children }) {
  return (
    <div className="flex flex-col gap-4 p-5 rounded-lg bg-surface border border-border">
      <div className="flex items-baseline gap-3">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-text-muted tabular-nums">
          Q{index}
          {mode === 'multi' && (
            <span className="ml-2 text-text-secondary normal-case tracking-normal">
              (multi-select)
            </span>
          )}
        </span>
      </div>
      <p className="text-base md:text-lg font-medium text-text">{label}</p>
      <div className="flex flex-wrap gap-2 pt-1">{children}</div>
    </div>
  );
}

export default function AboutYou() {
  const navigate = useNavigate();
  const { data, update } = useOnboarding();

  const canContinue =
    data.pressureResponse.length > 0 && data.conflictResponse.length > 0;

  const toggleGrowthArea = (area) => {
    const current = data.growthAreas;
    if (current.includes(area)) {
      update({ growthAreas: current.filter((g) => g !== area) });
    } else if (current.length < 3) {
      update({ growthAreas: [...current, area] });
    }
  };

  return (
    <OnboardingLayout
      step={3}
      footer={
        <>
          <Button
            variant="ghost"
            onClick={() => navigate('/onboarding/profile')}
          >
            <ArrowLeft size={18} /> Back
          </Button>
          <Button
            variant="primary"
            disabled={!canContinue}
            onClick={() => navigate('/onboarding/ready')}
          >
            Continue <ArrowRight size={18} />
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-7 max-w-2xl mx-auto py-4">
        <header className="flex flex-col gap-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-primary">
            About You
          </span>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            A few quick questions.
          </h1>
          <p className="text-sm text-text-secondary">
            There are no right answers.
          </p>
        </header>

        <div className="flex flex-col gap-4">
          <QuestionCard index={1} label="Under pressure, you tend to...">
            {pressureOptions.map((opt) => (
              <PillButton
                key={opt}
                active={data.pressureResponse === opt}
                onClick={() => update({ pressureResponse: opt })}
              >
                {opt}
              </PillButton>
            ))}
          </QuestionCard>

          <QuestionCard
            index={2}
            label="When you disagree with someone, you..."
          >
            {conflictOptions.map((opt) => (
              <PillButton
                key={opt}
                active={data.conflictResponse === opt}
                onClick={() => update({ conflictResponse: opt })}
              >
                {opt}
              </PillButton>
            ))}
          </QuestionCard>

          <QuestionCard
            index={3}
            mode="multi"
            label="What do you want to improve? (pick up to 3)"
          >
            {growthAreaOptions.map((opt) => (
              <PillButton
                key={opt}
                mode="multi"
                active={data.growthAreas.includes(opt)}
                onClick={() => toggleGrowthArea(opt)}
              >
                {opt}
              </PillButton>
            ))}
          </QuestionCard>
        </div>
      </div>
    </OnboardingLayout>
  );
}

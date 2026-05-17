import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import Button from '../components/Button.jsx';
import Input from '../components/Input.jsx';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    // No real auth yet — just go to onboarding.
    navigate('/onboarding/welcome');
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12">
      {/* Soft ambient glow */}
      <div
        className="pointer-events-none fixed inset-0 -z-10"
        style={{
          background:
            'radial-gradient(circle at 50% 30%, rgba(168, 85, 247, 0.15), transparent 60%)',
        }}
      />

      <div className="w-full max-w-md flex flex-col gap-8 animate-fade-in">
        {/* Logo + branding */}
        <header className="flex flex-col items-center gap-4">
          <img
            src="/images/LDM.svg"
            alt="LDM"
            style={{ height: 56, width: 'auto' }}
            draggable={false}
          />
          <p className="text-sm text-text-secondary">
            Leadership in 5 personas.
          </p>
        </header>

        {/* Login card */}
        <form
          onSubmit={handleLogin}
          className="flex flex-col gap-5 p-7 rounded-lg bg-surface border border-border"
        >
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Button type="submit" variant="primary" size="md" className="w-full mt-2">
            Log in
          </Button>

          <div className="flex items-center gap-3 text-xs text-text-muted">
            <div className="flex-1 h-px bg-divider" />
            <span>or</span>
            <div className="flex-1 h-px bg-divider" />
          </div>

          <Button type="button" variant="ghost" size="md" className="w-full">
            Continue with Google
          </Button>
        </form>

        <p className="text-center text-sm text-text-secondary">
          New here?{' '}
          <button
            type="button"
            onClick={() => navigate('/onboarding/welcome')}
            className="text-primary hover:text-primary-hover font-medium transition-colors"
          >
            Create an account
          </button>
        </p>
      </div>
    </main>
  );
}

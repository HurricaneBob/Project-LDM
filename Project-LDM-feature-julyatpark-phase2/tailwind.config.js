/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          hover: 'var(--color-primary-hover)',
        },
        secondary: {
          DEFAULT: 'var(--color-secondary)',
          hover: 'var(--color-secondary-hover)',
        },
        bg: 'var(--color-bg)',
        surface: {
          DEFAULT: 'var(--color-surface)',
          hi: 'var(--color-surface-hi)',
        },
        border: 'var(--color-border)',
        divider: 'var(--color-divider)',
        text: {
          DEFAULT: 'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
          muted: 'var(--color-text-muted)',
        },
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        info: 'var(--color-info)',
        persona: {
          commander: 'var(--color-persona-commander)',
          facilitator: 'var(--color-persona-facilitator)',
          strategist: 'var(--color-persona-strategist)',
          supporter: 'var(--color-persona-supporter)',
          adaptive: 'var(--color-persona-adaptive)',
        },
      },
      fontFamily: {
        sans: ['Pretendard', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'glow-pulse': {
          '0%, 100%': { opacity: '0.8' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 400ms ease-out forwards',
        'glow-pulse': 'glow-pulse 2.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

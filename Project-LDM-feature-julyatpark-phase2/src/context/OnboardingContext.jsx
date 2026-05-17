import { createContext, useContext, useState, useEffect } from 'react';

const STORAGE_KEY = 'ldm_onboarding';

const defaultState = {
  name: '',
  role: '',
  experienceLevel: '',
  pressureResponse: '',
  conflictResponse: '',
  growthAreas: [],
};

const OnboardingContext = createContext(null);

export function OnboardingProvider({ children }) {
  const [data, setData] = useState(() => {
    if (typeof window === 'undefined') return defaultState;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      return stored ? { ...defaultState, ...JSON.parse(stored) } : defaultState;
    } catch {
      return defaultState;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      /* ignore quota errors */
    }
  }, [data]);

  const update = (patch) => setData((prev) => ({ ...prev, ...patch }));
  const reset = () => {
    setData(defaultState);
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  };

  return (
    <OnboardingContext.Provider value={{ data, update, reset }}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext);
  if (!ctx) throw new Error('useOnboarding must be used within OnboardingProvider');
  return ctx;
}

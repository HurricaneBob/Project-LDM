import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import { OnboardingProvider } from './context/OnboardingContext.jsx';
import { SessionProvider } from './context/SessionContext.jsx';
import './index.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <OnboardingProvider>
        <SessionProvider>
          <App />
        </SessionProvider>
      </OnboardingProvider>
    </BrowserRouter>
  </StrictMode>
);

import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './screens/Login.jsx';
import Welcome from './screens/onboarding/Welcome.jsx';
import Profile from './screens/onboarding/Profile.jsx';
import AboutYou from './screens/onboarding/AboutYou.jsx';
import Ready from './screens/onboarding/Ready.jsx';
import AppLayout from './components/AppLayout.jsx';
import Chat from './screens/Chat.jsx';
import History from './screens/History.jsx';
import Analysis from './screens/Analysis.jsx';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/onboarding" element={<Navigate to="/onboarding/welcome" replace />} />
      <Route path="/onboarding/welcome" element={<Welcome />} />
      <Route path="/onboarding/profile" element={<Profile />} />
      <Route path="/onboarding/about-you" element={<AboutYou />} />
      <Route path="/onboarding/ready" element={<Ready />} />

      <Route element={<AppLayout />}>
        <Route path="/" element={<Chat />} />
        <Route path="/history" element={<History />} />
        <Route path="/analysis" element={<Analysis />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { PanelLeftOpen } from 'lucide-react';
import Sidebar from './Sidebar.jsx';

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const toggle = () => setCollapsed((c) => !c);

  return (
    <div className="h-screen flex bg-bg overflow-hidden">
      <Sidebar collapsed={collapsed} onToggle={toggle} />
      <div className="flex-1 min-w-0 min-h-0 flex flex-col relative">
        {collapsed && (
          <button
            type="button"
            onClick={toggle}
            aria-label="Show sidebar"
            className="
              absolute top-4 left-4 z-10
              w-9 h-9 rounded-md
              bg-surface border border-border
              flex items-center justify-center
              text-text-secondary hover:text-text hover:bg-surface-hi
              transition-colors animate-fade-in
            "
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
        <Outlet />
      </div>
    </div>
  );
}

"use client";

import React from 'react';
import { 
  Compass, 
  GitFork, 
  Users, 
  Activity, 
  Settings, 
  LogOut 
} from 'lucide-react';

interface AppSidebarProps {
  activeView: 'feed' | 'canvas' | 'cohort' | 'analytics';
  onSelectView: (view: 'feed' | 'canvas' | 'cohort' | 'analytics') => void;
  userEmail: string | null;
  onSignOut: () => void;
  completedCount?: number;
  totalCount?: number;
}

interface NavItem {
  id: 'feed' | 'canvas' | 'cohort' | 'analytics';
  label: string;
  icon: React.ElementType;
  badge?: string;
}

export function AppSidebar({
  activeView,
  onSelectView,
  userEmail,
  onSignOut,
  completedCount = 0,
  totalCount = 0,
}: AppSidebarProps) {
  const navItems: NavItem[] = [
    { id: 'feed', label: 'Curriculum Feed', icon: Compass },
    { id: 'canvas', label: 'Visual Graph', icon: GitFork },
    { 
      id: 'cohort', 
      label: 'Study Cohort', 
      icon: Users,
      badge: 'Live' 
    },
    { 
      id: 'analytics', 
      label: 'Proficiency Radar', 
      icon: Activity,
      badge: totalCount > 0 ? `${completedCount}/${totalCount}` : undefined 
    },
  ];

  const initials = userEmail 
    ? userEmail.slice(0, 2).toUpperCase() 
    : 'LP';

  return (
    <aside className="w-60 shrink-0 border-r border-border bg-sidebar flex flex-col justify-between h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div>
        <div className="h-16 px-6 flex items-center border-b border-border/60">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-bold text-xs tracking-wider">
              PF
            </div>
            <span className="font-extrabold tracking-tight text-lg text-foreground font-sans">
              PATHFINDER
            </span>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive 
                    ? 'bg-card text-foreground shadow-xs font-semibold' 
                    : 'text-muted-foreground hover:text-foreground hover:bg-card/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-primary' : 'text-muted-foreground'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-muted text-foreground/80 font-normal">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer / User Profile & Settings */}
      <div className="p-3 border-t border-border/60 space-y-2">
        <div className="flex items-center justify-between px-3 py-2 rounded-lg text-xs text-muted-foreground">
          <span className="flex items-center gap-2">
            <Settings className="w-3.5 h-3.5" />
            <span>Settings</span>
          </span>
          <span className="text-[10px] text-muted-foreground/70">v2.4</span>
        </div>

        <div className="flex items-center justify-between p-2 rounded-lg bg-card/60 border border-border/40">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-foreground truncate">
                {userEmail || 'Learner'}
              </p>
              <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                <span>Active Track</span>
              </div>
            </div>
          </div>
          <button
            onClick={onSignOut}
            title="Sign out"
            className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-destructive transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}

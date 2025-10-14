'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Building2,
  User,
  BarChart3,
  FileText,
  Activity,
  Dumbbell,
  TrendingUp,
  Settings,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth';
import { useRouter } from 'next/navigation';

const menuItems = [
  { href: '/dashboard', label: 'Organizations', icon: Building2 },
  { href: '/dashboard/personal-twin', label: 'Personal Twin', icon: User },
  { href: '/dashboard/bia', label: 'BIA Analysis', icon: BarChart3 },
  { href: '/dashboard/scenarios', label: 'Scenarios', icon: FileText },
  { href: '/dashboard/simulations', label: 'Simulations', icon: Activity },
  { href: '/dashboard/exercises', label: 'Exercises', icon: Dumbbell },
  { href: '/dashboard/predictions', label: 'Predictions', icon: TrendingUp },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">Digital Twin</h1>
        <p className="text-xs text-gray-400 mt-1">BCM Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <User size={20} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.username}</p>
            <p className="text-xs text-gray-400">Logged in</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

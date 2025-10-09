'use client';

import { Sidebar } from '@/components/layout/sidebar';
import { useAuthStore } from '@/lib/store/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

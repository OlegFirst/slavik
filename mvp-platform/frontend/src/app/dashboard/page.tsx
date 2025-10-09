'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, checkAuth, logout } = useAuthStore();
  const [organization, setOrganization] = useState<any>(null);
  const [biaList, setBiaList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    try {
      const org = await api.getMyOrganization();
      setOrganization(org);

      if (org) {
        const bias = await api.listBIAs(org.id);
        setBiaList(bias);
      }
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleCreateOrganization = () => {
    router.push('/organizations/create');
  };

  const handleCreateBIA = () => {
    if (!organization) return;
    router.push(`/organizations/${organization.id}/bia/create`);
  };

  if (isLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">AI Platform ISO 22301</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold mb-8">Dashboard</h2>

        {/* Organization Section */}
        <section className="mb-8">
          <h3 className="text-xl font-semibold mb-4">Organization</h3>
          {organization ? (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h4 className="text-lg font-medium mb-2">{organization.name}</h4>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Industry:</span> {organization.industry || 'N/A'}
                </div>
                <div>
                  <span className="font-medium">Size:</span> {organization.size || 'N/A'} employees
                </div>
                <div>
                  <span className="font-medium">Processes:</span> {organization.stats?.processes_count || 0}
                </div>
                <div>
                  <span className="font-medium">BIA Analyses:</span> {organization.stats?.bia_analyses_count || 0}
                </div>
              </div>
              <div className="mt-4">
                <button
                  onClick={handleCreateBIA}
                  className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
                >
                  Create New BIA
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-gray-600 mb-4">You haven't created an organization yet.</p>
              <button
                onClick={handleCreateOrganization}
                className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
              >
                Create Organization
              </button>
            </div>
          )}
        </section>

        {/* BIA Section */}
        {organization && (
          <section>
            <h3 className="text-xl font-semibold mb-4">BIA Analyses</h3>
            {biaList.length > 0 ? (
              <div className="grid gap-4">
                {biaList.map((bia) => (
                  <div
                    key={bia.id}
                    className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => router.push(`/organizations/${organization.id}/bia/${bia.id}`)}
                  >
                    <h4 className="text-lg font-medium mb-2">{bia.name}</h4>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {bia.status}
                      </span>
                      <span>Method: {bia.collection_method}</span>
                      <span>Score: {bia.compliance_score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <p className="text-gray-600">No BIA analyses yet. Create one to get started.</p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

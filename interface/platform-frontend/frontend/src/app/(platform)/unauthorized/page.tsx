'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { ShieldAlert, Home, LogOut, Mail, ArrowLeft, Lock, User } from 'lucide-react';

export default function UnauthorizedPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [reason, setReason] = useState<string>('');
  const [requiredRole, setRequiredRole] = useState<string>('');
  const [currentUser, setCurrentUser] = useState<string>('');

  useEffect(() => {
    // Get reason from URL params or storage
    const urlReason = searchParams.get('reason');
    const urlRole = searchParams.get('role');
    const urlUser = searchParams.get('user');

    setReason(urlReason || 'You do not have permission to access this resource.');
    setRequiredRole(urlRole || '');
    setCurrentUser(urlUser || '');
  }, [searchParams]);

  const handleRequestAccess = () => {
    const subject = encodeURIComponent('Access Request - AI Platform ISO 22301');
    const body = encodeURIComponent(`
I would like to request access to a restricted resource.

Resource: ${window.location.href}
${requiredRole ? `Required Role: ${requiredRole}` : ''}
Current User: ${currentUser || 'Not specified'}
Reason for Access:

[Please describe why you need access to this resource]
    `.trim());

    window.location.href = `mailto:admin@aiplatform.com?subject=${subject}&body=${body}`;
  };

  const handleLogout = () => {
    // Clear authentication and redirect to login
    localStorage.removeItem('authToken');
    sessionStorage.clear();
    router.push('/login');
  };

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border-2 border-orange-100">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-500 via-orange-500 to-amber-500 p-8 text-white">
            <div className="flex items-start gap-4">
              {/* Animated Icon */}
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-white/20 rounded-full blur-xl animate-pulse" />
                <div className="relative bg-white/20 backdrop-blur-sm rounded-full p-4">
                  <ShieldAlert className="w-12 h-12 text-white" />
                </div>
              </div>

              <div className="flex-1">
                <h1 className="text-3xl font-bold mb-2">
                  Access Denied
                </h1>
                <p className="text-orange-100 text-lg">
                  You don't have permission to view this page.
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            {/* Reason */}
            <div className="mb-6 p-4 bg-orange-50 border-2 border-orange-100 rounded-lg">
              <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Why can't I access this?
              </h3>
              <p className="text-foreground">{reason}</p>
            </div>

            {/* Required Role */}
            {requiredRole && (
              <div className="mb-6 p-4 bg-amber-50 border-2 border-amber-100 rounded-lg">
                <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Required Permission
                </h3>
                <p className="text-foreground font-semibold">{requiredRole}</p>
              </div>
            )}

            {/* Current User Info */}
            {currentUser && (
              <div className="mb-6 text-sm text-muted-foreground">
                Currently signed in as: <span className="font-medium text-foreground">{currentUser}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3 mb-6">
              <button
                onClick={handleRequestAccess}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl"
              >
                <Mail className="w-4 h-4" />
                Request Access
              </button>

              <button
                onClick={handleLogout}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-orange-200 hover:border-orange-300 text-foreground font-medium rounded-lg transition-all"
              >
                <LogOut className="w-4 h-4" />
                Sign in as Different User
              </button>

              <div className="flex gap-3">
                <button
                  onClick={() => router.back()}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 hover:border-gray-300 text-foreground font-medium rounded-lg transition-all"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Go Back
                </button>

                <Link
                  href="/dashboard"
                  className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 hover:border-gray-300 text-foreground font-medium rounded-lg transition-all"
                >
                  <Home className="w-4 h-4" />
                  Dashboard
                </Link>
              </div>
            </div>

            {/* Help Section */}
            <div className="p-4 bg-muted/30 rounded-lg">
              <h3 className="text-sm font-medium text-foreground mb-2">
                Need help getting access?
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                Contact your system administrator or send an access request. Include details about what you need to access and why.
              </p>
              <div className="flex flex-wrap gap-4 text-sm">
                <a
                  href="mailto:admin@aiplatform.com"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  admin@aiplatform.com
                </a>
                <Link
                  href="/help/permissions"
                  className="text-orange-600 hover:text-orange-700 underline"
                >
                  Learn about permissions
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>
            If you believe this is a mistake, please contact your administrator.
          </p>
        </div>
      </div>
    </div>
  );
}

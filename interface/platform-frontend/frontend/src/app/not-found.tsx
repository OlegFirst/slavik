import Link from 'next/link';
import { FileQuestion, Home, FileText, Shield, Brain, Search, ArrowLeft, AlertCircle } from 'lucide-react';

export const metadata = {
  title: '404 - Page Not Found | AI Platform ISO 22301',
  description: 'The page you are looking for could not be found.',
};

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-4xl w-full">
        {/* Breadcrumb */}
        <div className="mb-8 text-sm text-muted-foreground">
          <Link href="/" className="hover:text-foreground transition-colors">
            Home
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">404 Not Found</span>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Left Column - Error Message */}
            <div className="p-8 md:p-12 flex flex-col justify-center">
              {/* Animated Icon */}
              <div className="mb-8 flex justify-center md:justify-start">
                <div className="relative">
                  <div className="absolute inset-0 bg-orange-400/20 rounded-full blur-xl animate-pulse" />
                  <div className="relative bg-gradient-to-br from-orange-500 to-amber-600 rounded-full p-6">
                    <FileQuestion className="w-16 h-16 text-white" />
                  </div>
                </div>
              </div>

              {/* 404 Text */}
              <div className="mb-6">
                <h1 className="text-7xl md:text-8xl font-bold bg-gradient-to-r from-orange-600 via-amber-600 to-yellow-600 bg-clip-text text-transparent mb-4">
                  404
                </h1>
                <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
                  Page Not Found
                </h2>
                <p className="text-lg text-muted-foreground">
                  We couldn't find the page you're looking for. It might have been moved, deleted, or the URL might be incorrect.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Link
                  href="/"
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl"
                >
                  <Home className="w-4 h-4" />
                  Go Home
                </Link>
                <button
                  onClick={() => window.history.back()}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-orange-200 hover:border-orange-300 text-foreground font-medium rounded-lg transition-all"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Go Back
                </button>
              </div>

              {/* Report Link */}
              <a
                href="mailto:support@aiplatform.com?subject=Broken Link Report"
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-orange-600 transition-colors"
              >
                <AlertCircle className="w-4 h-4" />
                Report a broken link
              </a>
            </div>

            {/* Right Column - Quick Links & Search */}
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-8 md:p-12">
              {/* Search Bar */}
              <div className="mb-8">
                <label htmlFor="search" className="block text-sm font-medium text-foreground mb-3">
                  Search for what you need
                </label>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    id="search"
                    type="text"
                    placeholder="Search documentation, guides..."
                    className="w-full pl-12 pr-4 py-3 bg-white border-2 border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const searchTerm = e.currentTarget.value;
                        window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
                      }
                    }}
                  />
                </div>
              </div>

              {/* Common Links */}
              <div>
                <h3 className="text-sm font-medium text-foreground mb-4">
                  Common destinations
                </h3>
                <div className="space-y-3">
                  <Link
                    href="/dashboard"
                    className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-all group"
                  >
                    <div className="p-2 bg-gradient-to-br from-orange-100 to-amber-100 rounded-lg group-hover:from-orange-200 group-hover:to-amber-200 transition-colors">
                      <Home className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <div className="font-medium text-foreground">Dashboard</div>
                      <div className="text-sm text-muted-foreground">View your overview</div>
                    </div>
                  </Link>

                  <Link
                    href="/documents"
                    className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-all group"
                  >
                    <div className="p-2 bg-gradient-to-br from-orange-100 to-amber-100 rounded-lg group-hover:from-orange-200 group-hover:to-amber-200 transition-colors">
                      <FileText className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <div className="font-medium text-foreground">Documents</div>
                      <div className="text-sm text-muted-foreground">Browse documentation</div>
                    </div>
                  </Link>

                  <Link
                    href="/bia"
                    className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-all group"
                  >
                    <div className="p-2 bg-gradient-to-br from-orange-100 to-amber-100 rounded-lg group-hover:from-orange-200 group-hover:to-amber-200 transition-colors">
                      <Shield className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <div className="font-medium text-foreground">BIA Analysis</div>
                      <div className="text-sm text-muted-foreground">Business Impact Analysis</div>
                    </div>
                  </Link>

                  <Link
                    href="/ai"
                    className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-all group"
                  >
                    <div className="p-2 bg-gradient-to-br from-orange-100 to-amber-100 rounded-lg group-hover:from-orange-200 group-hover:to-amber-200 transition-colors">
                      <Brain className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <div className="font-medium text-foreground">AI Assistant</div>
                      <div className="text-sm text-muted-foreground">Get intelligent help</div>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Help Text */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            Need help? Contact{' '}
            <a href="mailto:support@aiplatform.com" className="text-orange-600 hover:text-orange-700 underline">
              support@aiplatform.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

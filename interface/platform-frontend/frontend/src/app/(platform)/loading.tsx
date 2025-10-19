import { Loader2 } from 'lucide-react';

export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] px-4 py-12">
      {/* Main Loading Spinner */}
      <div className="mb-8">
        <div className="relative">
          {/* Outer pulse ring */}
          <div className="absolute inset-0 bg-orange-400/20 rounded-full blur-2xl animate-pulse" />

          {/* Spinning loader */}
          <div className="relative">
            <Loader2 className="w-16 h-16 text-orange-500 animate-spin" />
          </div>
        </div>
      </div>

      {/* Loading Text */}
      <h2 className="text-xl font-semibold text-foreground mb-2">
        Loading...
      </h2>
      <p className="text-muted-foreground text-center max-w-md">
        Please wait while we prepare your content
      </p>

      {/* Progress Bar */}
      <div className="w-full max-w-xs mt-8">
        <div className="h-2 bg-orange-100 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-orange-500 to-amber-600 animate-indeterminate w-1/4" />
        </div>
      </div>

      {/* Skeleton Content Preview */}
      <div className="w-full max-w-4xl mt-16 space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 bg-gradient-to-br from-orange-200 to-amber-200 rounded-lg animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-6 bg-gradient-to-r from-orange-200 to-amber-200 rounded w-1/3 animate-pulse" />
            <div className="h-4 bg-gradient-to-r from-orange-100 to-amber-100 rounded w-1/2 animate-pulse" />
          </div>
        </div>

        {/* Content Cards Skeleton */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-xl p-6 border-2 border-orange-100 space-y-4"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-orange-200 to-amber-200 rounded-lg animate-pulse" />
                <div className="h-5 bg-gradient-to-r from-orange-200 to-amber-200 rounded w-2/3 animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gradient-to-r from-orange-100 to-amber-100 rounded w-full animate-pulse" />
                <div className="h-4 bg-gradient-to-r from-orange-100 to-amber-100 rounded w-5/6 animate-pulse" />
                <div className="h-4 bg-gradient-to-r from-orange-100 to-amber-100 rounded w-4/6 animate-pulse" />
              </div>
              <div className="pt-2 flex gap-2">
                <div className="h-8 w-20 bg-gradient-to-r from-orange-200 to-amber-200 rounded animate-pulse" />
                <div className="h-8 w-20 bg-gradient-to-r from-orange-100 to-amber-100 rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>

        {/* List Skeleton */}
        <div className="bg-white rounded-xl border-2 border-orange-100 overflow-hidden">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="p-6 border-b border-orange-50 last:border-b-0 flex items-center gap-4"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="h-12 w-12 bg-gradient-to-br from-orange-200 to-amber-200 rounded-full animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gradient-to-r from-orange-200 to-amber-200 rounded w-1/4 animate-pulse" />
                <div className="h-3 bg-gradient-to-r from-orange-100 to-amber-100 rounded w-3/4 animate-pulse" />
              </div>
              <div className="h-8 w-24 bg-gradient-to-r from-orange-200 to-amber-200 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

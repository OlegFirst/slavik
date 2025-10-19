# Loading Components

A comprehensive suite of production-ready loading and skeleton components for the AI Platform interface.

## Components

### LoadingSpinner
Configurable loading spinner with size and color variants.

```tsx
import { LoadingSpinner } from '@/components/loading';

// Basic usage
<LoadingSpinner />

// With label
<LoadingSpinner size="md" color="primary" label="Loading..." />

// Centered
<LoadingSpinner size="lg" centered />

// Different sizes and colors
<LoadingSpinner size="sm" color="white" />
<LoadingSpinner size="xl" color="secondary" />
```

**Props:**
- `size`: 'sm' | 'md' | 'lg' | 'xl' (default: 'md')
- `color`: 'primary' | 'secondary' | 'white' (default: 'primary')
- `label`: Optional text label
- `centered`: Center the spinner (default: false)
- `ariaLabel`: Accessible label for screen readers

### LoadingSkeleton
Flexible skeleton loader with animated shimmer effect.

```tsx
import { LoadingSkeleton } from '@/components/loading';

// Text skeleton
<LoadingSkeleton variant="text" width={200} />

// Multiple lines
<LoadingSkeleton variant="text" lines={3} />

// Circle (avatar)
<LoadingSkeleton variant="circle" size={40} />

// Rectangle
<LoadingSkeleton variant="rectangle" width={300} height={200} />

// Card
<LoadingSkeleton variant="card" />
```

**Props:**
- `variant`: 'text' | 'circle' | 'rectangle' | 'card' (default: 'text')
- `width`: Width in pixels or string
- `height`: Height in pixels or string
- `size`: Size for circle variant
- `lines`: Number of lines for text variant (default: 1)

### PageLoader
Full-page loading screen with overlay.

```tsx
import { PageLoader } from '@/components/loading';

// Basic usage
<PageLoader message="Loading application..." />

// With progress
<PageLoader message="Processing..." progress={75} />

// Without logo
<PageLoader showLogo={false} />
```

**Props:**
- `message`: Loading message to display
- `showLogo`: Show logo/branding (default: true)
- `progress`: Progress value 0-100 for progress bar

### ProgressBar
Progress indicator with linear and circular variants.

```tsx
import { ProgressBar } from '@/components/loading';

// Determinate progress
<ProgressBar value={75} max={100} />

// With percentage display
<ProgressBar value={50} showPercentage />

// Indeterminate loading
<ProgressBar indeterminate />

// Circular variant
<ProgressBar value={30} variant="circular" size="lg" />

// Different colors
<ProgressBar value={80} color="success" />
<ProgressBar value={40} color="warning" />
```

**Props:**
- `value`: Current progress value
- `max`: Maximum value (default: 100)
- `indeterminate`: Indeterminate loading state
- `variant`: 'linear' | 'circular' (default: 'linear')
- `color`: 'primary' | 'secondary' | 'success' | 'warning' (default: 'primary')
- `size`: 'sm' | 'md' | 'lg' (default: 'md')
- `showPercentage`: Display percentage text

### CardSkeleton
Skeleton loader matching DocumentCard layout.

```tsx
import { CardSkeleton } from '@/components/loading';

// Single card
<CardSkeleton />

// Multiple cards
<CardSkeleton count={3} />

// Without footer
<CardSkeleton showFooter={false} />
```

**Props:**
- `count`: Number of cards to display (default: 1)
- `showHeader`: Show header skeleton (default: true)
- `showFooter`: Show footer skeleton (default: true)

### TableSkeleton
Skeleton loader for table views.

```tsx
import { TableSkeleton } from '@/components/loading';

// Basic table
<TableSkeleton rows={5} columns={4} />

// With alternating rows
<TableSkeleton rows={10} columns={6} alternating />
```

**Props:**
- `rows`: Number of rows to display (default: 5)
- `columns`: Number of columns (default: 4)
- `alternating`: Show alternating row colors

### ListSkeleton
Skeleton loader for list views.

```tsx
import { ListSkeleton } from '@/components/loading';

// Basic list
<ListSkeleton items={5} />

// With avatar and actions
<ListSkeleton items={3} showAvatar showActions />

// Without actions
<ListSkeleton items={8} showActions={false} />
```

**Props:**
- `items`: Number of list items (default: 5)
- `showAvatar`: Show avatar (default: true)
- `showActions`: Show action buttons (default: true)

## Usage Examples

### Loading State in Component

```tsx
'use client';

import { useState, useEffect } from 'react';
import { LoadingSpinner, CardSkeleton } from '@/components/loading';

export default function DataList() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchData().then(result => {
      setData(result);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <CardSkeleton count={3} />;
  }

  return (
    <div>
      {data.map(item => (
        <Card key={item.id} {...item} />
      ))}
    </div>
  );
}
```

### Full Page Loading

```tsx
'use client';

import { PageLoader } from '@/components/loading';
import { useState } from 'react';

export default function App() {
  const [initializing, setInitializing] = useState(true);

  if (initializing) {
    return <PageLoader message="Initializing application..." />;
  }

  return <MainApp />;
}
```

### Upload Progress

```tsx
'use client';

import { ProgressBar } from '@/components/loading';
import { useState } from 'react';

export default function FileUpload() {
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file: File) => {
    // Upload with progress tracking
    await uploadFile(file, (p) => setProgress(p));
  };

  return (
    <div>
      <ProgressBar
        value={progress}
        max={100}
        showPercentage
        color="primary"
      />
    </div>
  );
}
```

## Accessibility

All components include proper ARIA attributes:
- `role="status"` for loading indicators
- `aria-label` for screen reader context
- `aria-live="polite"` for dynamic updates
- `aria-valuenow`, `aria-valuemin`, `aria-valuemax` for progress bars

## Styling

Components use Anthropic warm color palette:
- Primary: Orange (#f97316)
- Secondary: Amber (#d97706)
- Background gradients: orange-50 to amber-100

All animations are configured in `tailwind.config.js`:
- `shimmer`: 2s infinite for skeleton loaders
- `fadeIn`: 0.3s for page loader
- `indeterminate`: 1.5s infinite for progress bars
- `spin`: Built-in Tailwind animation for spinners

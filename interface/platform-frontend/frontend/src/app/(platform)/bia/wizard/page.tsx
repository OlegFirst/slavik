'use client';

/**
 * BIA Wizard Page
 * Complete BIA workflow using BIAWorkflowWizard component
 */

import { useRouter } from 'next/navigation';
import { BIAWorkflowWizard } from '@/components/bia';

export default function BIAWizardPage() {
  const router = useRouter();

  return (
    <BIAWorkflowWizard
      tenant_id="demo-tenant"
      onComplete={(processId) => {
        console.log('BIA Process created:', processId);
        router.push(`/bia/${processId}`);
      }}
      onCancel={() => {
        router.push('/bia');
      }}
      onSaveDraft={(data) => {
        console.log('Saving draft:', data);
        // TODO: Implement draft save to localStorage or API
        localStorage.setItem('bia-draft', JSON.stringify(data));
      }}
    />
  );
}

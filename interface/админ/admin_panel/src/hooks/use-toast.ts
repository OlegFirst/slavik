/**
 * Simple Toast Hook
 * =================
 */

export const useToast = () => {
  const toast = ({ title, description, variant }: { title: string; description?: string; variant?: 'default' | 'destructive' }) => {
    // Simple console logging for now - can be enhanced with a toast library
    const message = `${title}${description ? ': ' + description : ''}`;
    if (variant === 'destructive') {
      console.error(message);
      alert(message);
    } else {
      console.log(message);
    }
  };

  return { toast };
};

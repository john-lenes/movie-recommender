import { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

let toastId = 0;

const toastListeners: ((toast: Toast) => void)[] = [];
const removeListeners: ((id: number) => void)[] = [];

export const toast = {
  success: (message: string) => {
    const id = ++toastId;
    toastListeners.forEach(fn => fn({ id, message, type: 'success' }));
    setTimeout(() => removeListeners.forEach(fn => fn(id)), 3000);
  },
  error: (message: string) => {
    const id = ++toastId;
    toastListeners.forEach(fn => fn({ id, message, type: 'error' }));
    setTimeout(() => removeListeners.forEach(fn => fn(id)), 4000);
  },
  info: (message: string) => {
    const id = ++toastId;
    toastListeners.forEach(fn => fn({ id, message, type: 'info' }));
    setTimeout(() => removeListeners.forEach(fn => fn(id)), 3000);
  }
};

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const addToast = (toast: Toast) => {
      setToasts(prev => [...prev, toast]);
    };

    const removeToast = (id: number) => {
      setToasts(prev => prev.filter(t => t.id !== id));
    };

    toastListeners.push(addToast);
    removeListeners.push(removeToast);

    return () => {
      const addIdx = toastListeners.indexOf(addToast);
      if (addIdx > -1) toastListeners.splice(addIdx, 1);
      
      const removeIdx = removeListeners.indexOf(removeToast);
      if (removeIdx > -1) removeListeners.splice(removeIdx, 1);
    };
  }, []);

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map(({ id, message, type }) => (
        <div
          key={id}
          className={`
            p-4 rounded-xl shadow-xl backdrop-blur-sm animate-slide-in-right
            ${type === 'success' ? 'bg-green-500/90 text-white' : ''}
            ${type === 'error' ? 'bg-red-500/90 text-white' : ''}
            ${type === 'info' ? 'bg-blue-500/90 text-white' : ''}
          `}
        >
          <div className="flex items-center gap-2">
            <span className="text-xl">
              {type === 'success' && '✓'}
              {type === 'error' && '✕'}
              {type === 'info' && 'ℹ'}
            </span>
            <span className="font-medium">{message}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

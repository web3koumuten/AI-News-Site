import { clsx } from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'accent' | 'blue' | 'green' | 'gray';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
        {
          'bg-muted text-muted-foreground': variant === 'default',
          'bg-muted/50 text-foreground': variant === 'secondary',
          'bg-accent text-accent-foreground': variant === 'accent',
          'bg-blue-100 text-blue-800': variant === 'blue',
          'bg-green-100 text-green-800': variant === 'green',
          'bg-gray-100 text-gray-800': variant === 'gray',
        },
        className
      )}
    >
      {children}
    </span>
  );
}
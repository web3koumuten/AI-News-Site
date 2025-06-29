import { ReactNode } from 'react';
import { clsx } from 'clsx';

interface SectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function Section({ title, description, children, className }: SectionProps) {
  return (
    <section className={clsx('py-12', className)}>
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2">{title}</h2>
        {description && (
          <p className="text-muted-foreground">{description}</p>
        )}
      </div>
      {children}
    </section>
  );
}
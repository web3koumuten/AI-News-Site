import { ExternalLink, DollarSign } from 'lucide-react';
import { Card } from './Card';
import { Badge } from './Badge';
import type { AITool } from '@/types';
import { format } from 'date-fns';

interface ToolCardProps {
  tool: AITool;
}

export function ToolCard({ tool }: ToolCardProps) {
  const getPricingBadgeVariant = (type: string) => {
    switch (type) {
      case 'free':
        return 'accent';
      case 'freemium':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold mb-1">{tool.name}</h3>
          <Badge variant="secondary" className="mb-2">
            {tool.category}
          </Badge>
        </div>
        <a
          href={tool.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-accent transition-colors"
          aria-label={`Visit ${tool.name}`}
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
      
      <p className="text-sm text-muted-foreground mb-4 flex-grow">
        {tool.description}
      </p>
      
      <div className="space-y-3">
        {tool.features.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tool.features.slice(0, 3).map((feature, index) => (
              <Badge key={index} variant="default" className="text-xs">
                {feature}
              </Badge>
            ))}
            {tool.features.length > 3 && (
              <Badge variant="default" className="text-xs">
                +{tool.features.length - 3} more
              </Badge>
            )}
          </div>
        )}
        
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-muted-foreground" />
            <Badge variant={getPricingBadgeVariant(tool.pricing.type)}>
              {tool.pricing.type}
            </Badge>
            {tool.pricing.startingPrice && (
              <span className="text-xs text-muted-foreground">
                {tool.pricing.startingPrice}
              </span>
            )}
          </div>
          <span className="text-xs text-muted-foreground">
            {format(new Date(tool.updatedAt), 'MMM d')}
          </span>
        </div>
      </div>
    </Card>
  );
}
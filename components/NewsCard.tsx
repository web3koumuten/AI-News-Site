import { ExternalLink, Clock } from 'lucide-react';
import { Card } from './Card';
import { Badge } from './Badge';
import type { AINews } from '@/types';
import { format, formatDistanceToNow } from 'date-fns';

interface NewsCardProps {
  news: AINews;
}

export function NewsCard({ news }: NewsCardProps) {
  const publishedDate = new Date(news.publishedAt);
  const isRecent = Date.now() - publishedDate.getTime() < 24 * 60 * 60 * 1000; // 24 hours

  return (
    <Card className="h-full flex flex-col">
      <div className="flex items-start justify-between mb-3">
        <Badge variant="secondary" className="mb-2">
          {news.category}
        </Badge>
        <a
          href={news.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-accent transition-colors"
          aria-label="Read full article"
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      </div>
      
      <h3 className="text-lg font-semibold mb-2 line-clamp-2">
        {news.title}
      </h3>
      
      <p className="text-sm text-muted-foreground mb-4 flex-grow line-clamp-3">
        {news.summary}
      </p>
      
      <div className="space-y-3">
        {news.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {news.tags.map((tag, index) => (
              <Badge key={index} variant="default" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <span className="text-xs text-muted-foreground">
            {news.source}
          </span>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="w-3 h-3" />
            <span>
              {isRecent
                ? formatDistanceToNow(publishedDate, { addSuffix: true })
                : format(publishedDate, 'MMM d, yyyy')}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
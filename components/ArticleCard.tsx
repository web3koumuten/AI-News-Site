import Link from 'next/link';
import { Badge } from '@/components/Badge';
import type { NewsArticle, Tool } from '@/types';

interface ArticleCardProps {
  article: NewsArticle | Tool;
  type: 'news' | 'tool';
}

export function ArticleCard({ article, type }: ArticleCardProps) {
  const isNews = type === 'news';
  const newsArticle = article as NewsArticle;
  const toolArticle = article as Tool;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'technology':
      case 'tech':
        return 'bg-blue-100 text-blue-800';
      case 'ai_general':
      case 'ai':
        return 'bg-purple-100 text-purple-800';
      case 'research':
        return 'bg-green-100 text-green-800';
      case 'business':
        return 'bg-orange-100 text-orange-800';
      case 'machine_learning':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPricingColor = (type: string) => {
    switch (type) {
      case 'free':
        return 'bg-green-100 text-green-800';
      case 'freemium':
        return 'bg-blue-100 text-blue-800';
      case 'paid':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <article className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 p-6 mb-6 group">
      <header className="mb-4">
        <div className="flex items-center gap-2 mb-3">
          <Badge 
            className={getCategoryColor(isNews ? newsArticle.category : toolArticle.category)}
          >
            {isNews ? newsArticle.category : toolArticle.category}
          </Badge>
          {!isNews && (
            <Badge 
              className={getPricingColor(toolArticle.pricing.type)}
            >
              {toolArticle.pricing.type}
              {toolArticle.pricing.startingPrice && ` - ${toolArticle.pricing.startingPrice}`}
            </Badge>
          )}
          {isNews && newsArticle.tags && newsArticle.tags.length > 0 && (
            <>
              {newsArticle.tags.slice(0, 3).map((tag, index) => (
                <Badge 
                  key={index}
                  className="bg-gray-100 text-gray-700 text-xs"
                >
                  {tag}
                </Badge>
              ))}
            </>
          )}
        </div>
        
        <h2 className="text-xl font-bold text-gray-900 mb-2 leading-tight">
          <Link 
            href={`/article/${article.id}`}
            className="hover:text-blue-600 transition-colors duration-200 group-hover:text-blue-600"
          >
            {isNews ? newsArticle.title : toolArticle.name}
          </Link>
        </h2>
        
        <div className="flex items-center text-sm text-gray-500 mb-3">
          <time dateTime={isNews ? newsArticle.publishedAt : toolArticle.updatedAt}>
            {formatDate(isNews ? newsArticle.publishedAt : toolArticle.updatedAt)}
          </time>
          {isNews && (
            <>
              <span className="mx-2">•</span>
              <span>{newsArticle.source}</span>
            </>
          )}
        </div>
      </header>

      <div className="prose prose-gray max-w-none">
        <p className="text-gray-700 leading-relaxed mb-4">
          {isNews ? newsArticle.summary : toolArticle.description}
        </p>

        {!isNews && toolArticle.features && toolArticle.features.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">主な機能:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              {toolArticle.features.slice(0, 3).map((feature, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <footer className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
        <Link
          href={`/article/${article.id}`}
          className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors duration-200"
        >
          詳しく読む
          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
        
        <a
          href={isNews ? newsArticle.url : toolArticle.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center text-gray-500 hover:text-gray-700 text-sm transition-colors duration-200"
        >
          元記事
          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </footer>
    </article>
  );
}
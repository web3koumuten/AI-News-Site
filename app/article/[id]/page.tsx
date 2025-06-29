import { notFound } from 'next/navigation';
import Link from 'next/link';
import { promises as fs } from 'fs';
import path from 'path';
import type { UpdateData, Article } from '@/types';
import { Badge } from '@/components/Badge';
import { format } from 'date-fns';

interface ArticlePageProps {
  params: Promise<{
    id: string;
  }>;
}

async function getData(): Promise<UpdateData> {
  try {
    const dataPath = path.join(process.cwd(), 'data', 'ai_updates.json');
    const fileContents = await fs.readFile(dataPath, 'utf8');
    const data = JSON.parse(fileContents) as UpdateData;
    
    if (!data.tools || !Array.isArray(data.tools) || !data.news || !Array.isArray(data.news)) {
      throw new Error('Invalid data structure');
    }
    
    return data;
  } catch (error) {
    console.warn('Failed to load ai_updates.json, falling back to sample data:', error);
    
    try {
      const samplePath = path.join(process.cwd(), 'data', 'sample-data.json');
      const sampleContents = await fs.readFile(samplePath, 'utf8');
      return JSON.parse(sampleContents) as UpdateData;
    } catch {
      return {
        tools: [],
        news: [],
        lastUpdated: new Date().toISOString()
      };
    }
  }
}

function findArticleById(data: UpdateData, id: string): Article | null {
  // Search in tools
  const tool = data.tools.find(t => t.id === id);
  if (tool) {
    return { ...tool, type: 'tool' as const };
  }
  
  // Search in news
  const news = data.news.find(n => n.id === id);
  if (news) {
    return { ...news, type: 'news' as const };
  }
  
  return null;
}

function getCategoryDisplayName(category: string): string {
  const categoryMap: { [key: string]: string } = {
    'ai_coding': 'AI開発ツール',
    'ai_creative': 'AI画像・動画',
    'ai_writing': 'AI文章作成',
    'ai_assistant': 'AIアシスタント',
    'ai_general': 'AI一般',
    'technology': 'テクノロジー',
    'productivity': '生産性',
    'developer_tools': '開発者ツール'
  };
  
  return categoryMap[category] || category;
}

function getPricingDisplayText(pricing: { type: string; startingPrice?: string }): string {
  const typeMap: { [key: string]: string } = {
    'free': '無料',
    'freemium': 'フリーミアム',
    'paid': '有料'
  };
  
  const typeText = typeMap[pricing.type] || pricing.type;
  return pricing.startingPrice ? `${typeText} (${pricing.startingPrice}から)` : typeText;
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const resolvedParams = await params;
  const data = await getData();
  const article = findArticleById(data, resolvedParams.id);
  
  if (!article) {
    notFound();
  }
  
  // Get all articles for navigation
  const allArticles = [
    ...data.tools.map(tool => ({ ...tool, type: 'tool' as const, sortDate: tool.updatedAt })),
    ...data.news.map(news => ({ ...news, type: 'news' as const, sortDate: news.publishedAt }))
  ].sort((a, b) => new Date(b.sortDate).getTime() - new Date(a.sortDate).getTime());
  
  const currentIndex = allArticles.findIndex(a => a.id === resolvedParams.id);
  const previousArticle = currentIndex > 0 ? allArticles[currentIndex - 1] : null;
  const nextArticle = currentIndex < allArticles.length - 1 ? allArticles[currentIndex + 1] : null;
  
  const publishDate = article.type === 'tool' ? article.updatedAt : article.publishedAt;
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <Link 
              href="/"
              className="text-blue-600 hover:text-blue-700 font-medium flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              AI Updates 72に戻る
            </Link>
            
            <div className="text-sm text-gray-500">
              {format(new Date(publishDate), 'yyyy年M月d日')}
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Article Header */}
        <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* Article Image */}
          {(article.type === 'news' ? article.imageUrl : article.logo) && (
            <div className="aspect-video w-full overflow-hidden">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={article.type === 'news' ? article.imageUrl! : article.logo!}
                alt={article.type === 'tool' ? article.name : article.title}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          
          <div className="p-8">
            {/* Category and Type */}
            <div className="flex items-center gap-2 mb-4">
              <Badge variant={article.type === 'tool' ? 'blue' : 'green'}>
                {article.type === 'tool' ? 'ツール' : 'ニュース'}
              </Badge>
              <Badge variant="gray">
                {getCategoryDisplayName(article.category)}
              </Badge>
              {article.type === 'news' && article.source && (
                <Badge variant="gray">
                  {article.source}
                </Badge>
              )}
            </div>

            {/* Title */}
            <h1 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
              {article.type === 'tool' ? article.name : article.title}
            </h1>

            {/* Metadata */}
            <div className="flex items-center gap-4 text-sm text-gray-600 mb-6 pb-6 border-b border-gray-200">
              <time dateTime={publishDate}>
                {format(new Date(publishDate), 'yyyy年M月d日 HH:mm')}
              </time>
              
              {article.type === 'tool' && article.pricing && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                  {getPricingDisplayText(article.pricing)}
                </span>
              )}
              
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                元記事を見る
              </a>
            </div>

            {/* Summary */}
            <div className="prose prose-lg max-w-none mb-8">
              <p className="text-gray-700 leading-relaxed">
                {article.type === 'tool' ? article.description : article.summary}
              </p>
            </div>

            {/* Features (for tools) */}
            {article.type === 'tool' && article.features && article.features.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">主な機能</h3>
                <ul className="space-y-2">
                  {article.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Tags (for news) */}
            {article.type === 'news' && article.tags && article.tags.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">関連タグ</h3>
                <div className="flex flex-wrap gap-2">
                  {article.tags.map((tag, index) => (
                    <Badge key={index} variant="gray">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Full Content (if available) */}
            {article.content && article.content.length > (article.type === 'tool' ? article.description : article.summary).length && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">詳細</h3>
                <div className="prose max-w-none">
                  <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {article.content}
                  </div>
                </div>
              </div>
            )}
          </div>
        </article>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8 pt-8 border-t border-gray-200">
          {previousArticle ? (
            <Link
              href={`/article/${previousArticle.id}`}
              className="flex items-center text-blue-600 hover:text-blue-700 group"
            >
              <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div className="text-left">
                <div className="text-sm text-gray-500">前の記事</div>
                <div className="font-medium truncate max-w-xs">
                  {previousArticle.type === 'tool' ? previousArticle.name : previousArticle.title}
                </div>
              </div>
            </Link>
          ) : (
            <div></div>
          )}

          {nextArticle ? (
            <Link
              href={`/article/${nextArticle.id}`}
              className="flex items-center text-blue-600 hover:text-blue-700 group text-right"
            >
              <div className="text-right">
                <div className="text-sm text-gray-500">次の記事</div>
                <div className="font-medium truncate max-w-xs">
                  {nextArticle.type === 'tool' ? nextArticle.name : nextArticle.title}
                </div>
              </div>
              <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          ) : (
            <div></div>
          )}
        </div>
      </main>
    </div>
  );
}

export async function generateStaticParams() {
  try {
    const data = await getData();
    const allArticles = [
      ...data.tools.map(tool => ({ id: tool.id })),
      ...data.news.map(news => ({ id: news.id }))
    ];
    
    return allArticles;
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}
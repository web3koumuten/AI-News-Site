import Link from 'next/link';
import { Header } from '@/components/Header';
import { ArticleCard } from '@/components/ArticleCard';
import { Badge } from '@/components/Badge';
import type { UpdateData, NewsArticle, Tool } from '@/types';
import { promises as fs } from 'fs';
import path from 'path';

async function getData(): Promise<UpdateData> {
  try {
    // Try to load ai_updates.json first
    const dataPath = path.join(process.cwd(), 'data', 'ai_updates.json');
    const fileContents = await fs.readFile(dataPath, 'utf8');
    const data = JSON.parse(fileContents) as UpdateData;
    
    // Validate data structure
    if (!data.tools || !Array.isArray(data.tools) || !data.news || !Array.isArray(data.news)) {
      throw new Error('Invalid data structure');
    }
    
    return data;
  } catch (error) {
    console.warn('Failed to load ai_updates.json, falling back to sample data:', error);
    
    // Fallback to sample data
    try {
      const samplePath = path.join(process.cwd(), 'data', 'sample-data.json');
      const sampleContents = await fs.readFile(samplePath, 'utf8');
      return JSON.parse(sampleContents) as UpdateData;
    } catch (sampleError) {
      console.error('Failed to load sample data:', sampleError);
      
      // Ultimate fallback - return empty structure
      return {
        tools: [],
        news: [],
        lastUpdated: new Date().toISOString()
      };
    }
  }
}

export default async function Home() {
  const data = await getData();
  
  // Check if this is sample data or real data
  const isUsingSampleData = data.lastUpdated === new Date().toISOString() || 
    (data.tools.length > 0 && data.tools[0].name === 'Claude'); // Sample data indicator
  
  // Combine and sort all articles by date
  const allArticles = [
    ...data.tools.map(tool => ({ ...tool, type: 'tool' as const, sortDate: tool.updatedAt })),
    ...data.news.map(news => ({ ...news, type: 'news' as const, sortDate: news.publishedAt }))
  ].sort((a, b) => new Date(b.sortDate).getTime() - new Date(a.sortDate).getTime());
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Header lastUpdated={data.lastUpdated} />
      
      {/* Data Status Banner */}
      {isUsingSampleData && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
          <div className="container mx-auto">
            <div className="flex items-center justify-center text-sm text-yellow-800">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              現在サンプルデータを表示しています。最新の収集データは自動的にここに表示されます。
            </div>
          </div>
        </div>
      )}
      
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Blog Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Updates 72
          </h1>
          <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
            72時間ごとに更新される最新AIツール・サービスの情報をお届け
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
            {data.metadata && (
              <>
                <div className="bg-white px-4 py-2 rounded-full border border-gray-200">
                  📊 総記事数: {data.metadata.totalArticles}
                </div>
                <div className="bg-white px-4 py-2 rounded-full border border-gray-200">
                  🛠️ ツール: {data.metadata.toolsCount}
                </div>
                <div className="bg-white px-4 py-2 rounded-full border border-gray-200">
                  📰 ニュース: {data.metadata.newsCount}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Featured Article */}
        {allArticles.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm mr-3">Featured</span>
              注目の記事
            </h2>
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="p-8">
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant={allArticles[0].type === 'tool' ? 'blue' : 'green'}>
                    {allArticles[0].type === 'tool' ? 'ツール' : 'ニュース'}
                  </Badge>
                  <Badge variant="gray">
                    {allArticles[0].category}
                  </Badge>
                  <time className="text-sm text-gray-500">
                    {new Date(allArticles[0].sortDate).toLocaleDateString('ja-JP', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </time>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  <Link 
                    href={`/article/${allArticles[0].id}`}
                    className="hover:text-blue-600 transition-colors"
                  >
                    {allArticles[0].type === 'tool' ? allArticles[0].name : allArticles[0].title}
                  </Link>
                </h3>
                <p className="text-gray-700 text-lg leading-relaxed mb-6">
                  {allArticles[0].type === 'tool' ? allArticles[0].description : allArticles[0].summary}
                </p>
                <Link
                  href={`/article/${allArticles[0].id}`}
                  className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  記事を読む
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Categories Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-full text-sm font-medium">
              すべて
            </button>
            <button className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm border border-gray-200 hover:bg-gray-50">
              🛠️ AIツール
            </button>
            <button className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm border border-gray-200 hover:bg-gray-50">
              💻 コーディング
            </button>
            <button className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm border border-gray-200 hover:bg-gray-50">
              🎨 画像・動画
            </button>
            <button className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm border border-gray-200 hover:bg-gray-50">
              ✍️ 文章作成
            </button>
            <button className="px-4 py-2 bg-white text-gray-700 rounded-full text-sm border border-gray-200 hover:bg-gray-50">
              📰 ニュース
            </button>
          </div>
        </div>

        {/* Recent Articles Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            最新の記事
          </h2>
        </div>

        {/* Articles Grid */}
        {allArticles.length > 0 ? (
          <div className="space-y-6">
            {allArticles.slice(1).map((article, index) => (
              <div
                key={article.id}
                className="animate-fade-in"
                style={{ animationDelay: `${(index + 1) * 100}ms` }}
              >
                <ArticleCard 
                  article={article.type === 'tool' ? article as Tool : article as NewsArticle} 
                  type={article.type} 
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              まだデータがありません
            </h3>
            <p className="text-gray-600">
              AIニュースとツール情報を収集中です。しばらくお待ちください。
            </p>
          </div>
        )}
      </main>
      
      <footer className="border-t border-gray-200 mt-16 bg-white">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-gray-600 mb-2">
              AI Updates 72 - 72時間ごとに更新される日本のAI情報キュレーション
            </p>
            {!isUsingSampleData && (
              <p className="text-sm text-gray-500">
                最終更新: {new Date(data.lastUpdated).toLocaleString('ja-JP', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            )}
            <div className="mt-4 text-xs text-gray-400">
              {data.metadata?.sources && (
                <p>情報源: {data.metadata.sources.join(', ')}</p>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

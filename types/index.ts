export interface AITool {
  id: string;
  name: string;
  description: string;
  category: string;
  url: string;
  logo?: string;
  features: string[];
  pricing: {
    type: 'free' | 'freemium' | 'paid';
    startingPrice?: string;
  };
  updatedAt: string;
  content?: string; // Full article content for blog posts
  slug?: string; // URL-friendly slug for routing
}

export interface AINews {
  id: string;
  title: string;
  summary: string;
  source: string;
  url: string;
  publishedAt: string;
  category: string;
  imageUrl?: string;
  tags: string[];
  content?: string; // Full article content for blog posts
  slug?: string; // URL-friendly slug for routing
}

export interface UpdateData {
  tools: AITool[];
  news: AINews[];
  lastUpdated: string;
  metadata?: {
    totalArticles: number;
    toolsCount: number;
    newsCount: number;
    sources: string[];
    timeWindow: string;
    generatedAt: string;
  };
}

// Combined type for articles
export type Article = (AITool & { type: 'tool' }) | (AINews & { type: 'news' });

// For legacy compatibility
export type Tool = AITool;
export type NewsArticle = AINews;
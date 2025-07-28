<?php
/**
 * Plugin Name: AI News Site
 * Plugin URI: https://yourdomain.com/
 * Description: AI最新ニュースを表示するプラグイン
 * Version: 1.0
 * Author: Your Name
 */

// 直接アクセスを防ぐ
if (!defined('ABSPATH')) {
    exit;
}

// ショートコードを登録
add_shortcode('ai_news', 'ai_news_display');

function ai_news_display() {
    ob_start();
    ?>
    <style>
    #ai-news-container * {
        box-sizing: border-box !important;
    }
    
    #ai-news-container {
        font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif !important;
        line-height: 1.6 !important;
        color: #1a1a1a !important;
        background: #fafafa !important;
        padding: 60px 20px !important;
        margin: -40px -20px !important;
    }
    
    .ai-news-header {
        text-align: center !important;
        margin-bottom: 80px !important;
        position: relative !important;
    }
    
    .ai-news-title {
        font-size: clamp(3rem, 8vw, 6rem) !important;
        font-weight: 800 !important;
        color: #1a1a1a !important;
        margin-bottom: 20px !important;
        letter-spacing: -0.02em !important;
    }
    
    .ai-news-subtitle {
        color: #666666 !important;
        font-size: clamp(1.1rem, 3vw, 1.5rem) !important;
        font-weight: 400 !important;
        max-width: 700px !important;
        margin: 0 auto 40px !important;
    }
    
    .ai-news-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 12px 24px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 50px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    .ai-news-dot {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background: #10b981 !important;
        animation: blink 2s ease-in-out infinite !important;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .ai-news-grid {
        display: grid !important;
        gap: 40px !important;
        grid-template-columns: 1fr !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    .ai-news-card {
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 16px !important;
        padding: 48px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: block !important;
        color: inherit !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    .ai-news-card:hover {
        transform: translateY(-4px) !important;
        border-color: #6366f1 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    .ai-news-date {
        color: #06b6d4 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .ai-news-post-title {
        font-size: clamp(1.5rem, 4vw, 2rem) !important;
        font-weight: 700 !important;
        margin-bottom: 24px !important;
        color: #1a1a1a !important;
        line-height: 1.2 !important;
    }
    
    .ai-news-preview {
        color: #666666 !important;
        line-height: 1.7 !important;
        margin-bottom: 32px !important;
        font-size: 1.1rem !important;
    }
    
    .ai-news-read-more {
        display: inline-flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 12px 24px !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        border-radius: 50px !important;
        transition: all 0.3s ease !important;
    }
    
    .ai-news-read-more:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 16px 32px rgba(99, 102, 241, 0.3) !important;
    }
    
    .ai-news-footer {
        text-align: center !important;
        margin-top: 120px !important;
        padding: 48px !important;
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 16px !important;
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    @media (max-width: 768px) {
        #ai-news-container {
            padding: 40px 16px !important;
        }
        
        .ai-news-card {
            padding: 32px 24px !important;
        }
    }
    </style>
    
    <div id="ai-news-container">
        <header class="ai-news-header">
            <h1 class="ai-news-title">AI最新ニュース</h1>
            <p class="ai-news-subtitle">
                生成AI業界の今日の動きを厳選配信
            </p>
            <div class="ai-news-badge">
                <span class="ai-news-dot"></span>
                毎日更新
            </div>
        </header>

        <div class="ai-news-grid">
            <!-- 最新の投稿 -->
            <a href="<?php echo plugin_dir_url(__FILE__); ?>posts/2025-06-30.html" class="ai-news-card" target="_blank">
                <div class="ai-news-date">2025年6月30日</div>
                <h2 class="ai-news-post-title">24時間以内の生成AIニュース - 2025年6月30日</h2>
                <p class="ai-news-preview">
                    2025年6月30日の24時間以内に発表された生成AI業界の重要ニュースを厳選。NVIDIA関係者の10億ドル株式売却、OpenAIのGoogle AIチップ使用開始、Runway新ツール発表など、最新動向をコンパクトにまとめました。
                </p>
                <span class="ai-news-read-more">
                    詳細を読む
                    <span>→</span>
                </span>
            </a>

            <!-- 2日前の投稿 -->
            <a href="<?php echo plugin_dir_url(__FILE__); ?>posts/2025-06-29.html" class="ai-news-card" target="_blank">
                <div class="ai-news-date">2025年6月29日</div>
                <h2 class="ai-news-post-title">24時間以内の生成AIニュース - 2025年6月29日</h2>
                <p class="ai-news-preview">
                    2025年6月29日の24時間以内に発表された生成AI業界の重要ニュースを厳選。MetaのOpenAI人材引き抜き、AI著作権判決、Runway新ツール発表など、最新動向をコンパクトにまとめました。
                </p>
                <span class="ai-news-read-more">
                    詳細を読む
                    <span>→</span>
                </span>
            </a>

            <!-- 3日前の投稿 -->
            <a href="<?php echo plugin_dir_url(__FILE__); ?>posts/2025-06-28.html" class="ai-news-card" target="_blank">
                <div class="ai-news-date">2025年6月28日</div>
                <h2 class="ai-news-post-title">24時間以内の生成AIニュース - 2025年6月28日</h2>
                <p class="ai-news-preview">
                    OpenAIがGoogleチップ採用、人事の4割がAI活用、教育現場で課題浮上。6月28日の24時間で起こった生成AI重要ニュースを厳選。
                </p>
                <span class="ai-news-read-more">
                    詳細を読む
                    <span>→</span>
                </span>
            </a>
        </div>

        <footer class="ai-news-footer">
            <div class="ai-news-footer-content">
                <div style="font-weight: 700; color: #1a1a1a; margin-bottom: 16px; font-size: 1.2rem;">AI最新ニュース</div>
                <p style="color: #666666;">生成AI業界の重要な動向を毎日厳選してお届け</p>
                <p style="color: #666666;">OpenAI・Google・Meta・Anthropic等の最新発表を追跡</p>
            </div>
        </footer>
    </div>
    <?php
    return ob_get_clean();
}

// プラグイン有効化時にpostsフォルダを作成
register_activation_hook(__FILE__, 'ai_news_activate');

function ai_news_activate() {
    $upload_dir = wp_upload_dir();
    $plugin_dir = $upload_dir['basedir'] . '/ai-news-posts';
    
    if (!file_exists($plugin_dir)) {
        wp_mkdir_p($plugin_dir);
    }
}
?>
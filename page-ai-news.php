<?php
/**
 * Template Name: AI News Page
 * Description: AI最新ニュース専用ページテンプレート
 */

// ヘッダーとフッターなしで表示する場合
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>24時間以内の生成AI最新ニュース</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        /* ここに元のスタイルをそのまま貼り付け */
        body {
            font-family: 'Noto Sans JP', sans-serif;
        }
        .category-icon {
            width: 24px;
            height: 24px;
            margin-right: 12px;
        }
        .news-card {
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }
        .news-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .category-enterprise { border-left-color: #EF4444; }
        .category-tools { border-left-color: #10B981; }
        .category-legal { border-left-color: #8B5CF6; }
        .category-adoption { border-left-color: #3B82F6; }
        .category-market { border-left-color: #F59E0B; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- ここに元のHTMLコンテンツをそのまま貼り付け -->
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <!-- 以下、元のHTMLの内容 -->
    </div>
</body>
</html>
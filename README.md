# AI Updates 72 - 日本のAI情報キュレーション

日本のAIニュースとツール情報を72時間ごとに自動収集・表示するWebアプリケーションです。

## 機能

- **リアルタイム日本語AIニュース**: ITmedia AI+などの信頼できる日本の情報源から最新のAIニュースを収集
- **AIツール情報**: 新しいAIツールやサービスの情報を自動分類・表示
- **ブログ形式の表示**: カード形式ではなく、記事スタイルのHTMLレイアウト
- **自動更新**: 72時間ごとに最新情報を自動収集
- **日本語UI**: 完全日本語対応のユーザーインターフェース

## 技術スタック

### フロントエンド
- **Next.js 15**: React フレームワーク
- **TypeScript**: 型安全な開発
- **Tailwind CSS**: ユーティリティファーストのCSSフレームワーク
- **Lucide Icons**: モダンなアイコンセット

### バックエンド（スクレイパー）
- **Python 3.9+**: メインの開発言語
- **BeautifulSoup**: HTMLパースとWebスクレイピング
- **feedparser**: RSSフィード解析
- **Requests**: HTTP リクエスト処理

## 情報源

現在サポートしている日本のAI情報源：

1. **ITmedia AI+** - 日本のAI専門メディア (RSS)
2. **AI-SCHOLAR** - AI研究・技術情報 (RSS)
3. **Ledge.ai** - AIビジネス・事例情報 (RSS)
4. **AINOW** - AI専門ニュースメディア (RSS)
5. **ASCII.jp AI** - テクノロジーニュース (検索ベース)
6. **日経 AI** - ビジネス・経済観点のAI情報 (検索ベース)

## セットアップ

### 1. 依存関係のインストール

```bash
# フロントエンド
npm install

# バックエンド（スクレイパー）
cd scripts
pip install -r requirements.txt
```

### 2. 手動でのデータ収集

```bash
cd scripts
python3 main_scraper.py
```

### 3. 自動更新の設定

```bash
# 自動更新スクリプトの実行
cd scripts
./auto_update.sh
```

### 4. Webサイトの起動

```bash
# 開発サーバー
npm run dev

# プロダクションビルド
npm run build
npm start
```

## ファイル構造

```
ai-updates-72/
├── app/                    # Next.js アプリケーション
│   ├── page.tsx           # メインページ
│   ├── layout.tsx         # レイアウト
│   └── globals.css        # グローバルスタイル
├── components/            # React コンポーネント
│   ├── ArticleCard.tsx    # 記事表示コンポーネント
│   ├── Header.tsx         # ヘッダー
│   └── ...
├── scripts/              # Pythonスクレイパー
│   ├── main_scraper.py   # メインスクレイパー
│   ├── scrapers/         # 個別スクレイパー
│   ├── config.py         # 設定ファイル
│   ├── utils.py          # ユーティリティ関数
│   └── auto_update.sh    # 自動更新スクリプト
├── data/                 # データファイル
│   └── ai_updates.json   # 収集されたデータ
└── types/                # TypeScript型定義
    └── index.ts
```

## データ形式

収集されるデータの構造：

```json
{
  "tools": [
    {
      "id": "unique-id",
      "name": "ツール名",
      "description": "説明",
      "category": "カテゴリ",
      "url": "https://example.com",
      "features": ["機能1", "機能2"],
      "pricing": {
        "type": "free|freemium|paid",
        "startingPrice": "価格情報"
      },
      "updatedAt": "2025-06-28T15:33:23+09:00"
    }
  ],
  "news": [
    {
      "id": "unique-id",
      "title": "ニュースタイトル",
      "summary": "要約",
      "source": "情報源",
      "url": "https://example.com",
      "publishedAt": "2025-06-28T15:33:23+09:00",
      "category": "カテゴリ",
      "tags": ["タグ1", "タグ2"]
    }
  ],
  "lastUpdated": "2025-06-28T15:33:23+09:00",
  "metadata": {
    "totalArticles": 20,
    "toolsCount": 16,
    "newsCount": 4,
    "sources": ["itmedia", "ai_scholar", ...],
    "timeWindow": "72h"
  }
}
```

## 特徴

### 実際の日本語コンテンツ
- サンプルデータではなく、リアルタイムで収集された日本語のAI情報
- 過去72時間以内の最新情報のみを表示
- 重複記事の自動除去

### ブログ形式の表示
- カード形式ではなく、読みやすい記事スタイルのレイアウト
- 時系列での統合表示（ニュースとツール情報を混在）
- 日本語に最適化されたタイポグラフィ

### 自動分類
- AIツールか一般ニュースかの自動判別
- カテゴリの自動分類（技術、ビジネス、研究など）
- 価格情報の自動抽出（無料、フリーミアム、有料）

## カスタマイズ

### 新しい情報源の追加

`scripts/config.py`を編集して新しいソースを追加：

```python
SOURCES = {
    'new_source': {
        'name': '新しいソース名',
        'base_url': 'https://example.com/',
        'rss_url': 'https://example.com/feed/',
        'categories': ['category1', 'category2']
    }
}
```

対応するスクレイパーを`scripts/scrapers/`に作成し、`main_scraper.py`で登録します。

### 収集間隔の変更

`scripts/config.py`の`TIME_WINDOW`を変更：

```python
TIME_WINDOW = timedelta(hours=48)  # 48時間に変更
```

## 今後の改善予定

- [ ] より多くの日本語AI情報源の追加
- [ ] 検索・フィルタリング機能
- [ ] RSS配信機能
- [ ] メール通知機能
- [ ] 記事の全文表示機能
- [ ] ソーシャルメディア統合

## ライセンス

MIT License

## 貢献

プルリクエストや改善提案を歓迎します。新しい情報源の追加や機能改善など、お気軽にcontributeしてください。

---

**注意**: このツールは情報収集を目的としており、各サイトの利用規約を遵守して使用してください。スクレイピング頻度は適切に制限されています。
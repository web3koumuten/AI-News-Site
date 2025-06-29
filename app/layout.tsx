import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import "./globals.css";

const notoSansJP = Noto_Sans_JP({
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Updates 72 - Latest AI Tools & News",
  description: "Stay updated with the latest AI tools and news. Curated collection of artificial intelligence resources updated every 72 hours.",
  keywords: "AI tools, artificial intelligence, machine learning, AI news, AI updates",
  authors: [{ name: "AI Updates 72" }],
  openGraph: {
    title: "AI Updates 72",
    description: "Latest AI tools and news updated every 72 hours",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={notoSansJP.className}>
      <body className="antialiased">{children}</body>
    </html>
  );
}

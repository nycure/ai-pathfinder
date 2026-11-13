import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Pathfinder | Adaptive AI Learning Pathways",
  description: "Synthesize personalized, adaptive learning roadmaps powered by AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">{children}</body>
    </html>
  );
}

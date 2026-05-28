import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TaskHive — Secure Multi-Agent AI Task Automation",
  description:
    "AI swarm for secure autonomous web task execution. Five specialized agents collaborate to safely book tickets, pay bills, and complete real-world tasks with a security-first approach.",
  keywords: "multi-agent AI, autonomous web automation, secure booking, AI task swarm",
  openGraph: {
    title: "TaskHive — AI Task Swarm",
    description: "Secure multi-agent autonomous task execution platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Background effects */}
        <div className="bg-grid" aria-hidden="true" />
        <div className="bg-orb bg-orb-1" aria-hidden="true" />
        <div className="bg-orb bg-orb-2" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}

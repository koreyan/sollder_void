import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { Activity, ImageIcon, LayoutDashboard, Cpu } from "lucide-react";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Solder Void Detection Dashboard",
  description: "AI-Augmented Solder Void Detection System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <header style={{
            borderBottom: '1px solid var(--card-border)',
            backgroundColor: 'rgba(15, 17, 21, 0.8)',
            backdropFilter: 'blur(12px)',
            position: 'sticky',
            top: 0,
            zIndex: 50
          }}>
            <div className="container" style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              height: '64px'
            }}>
              <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Cpu size={24} color="var(--primary)" />
                <span style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em' }}>VoidDetect AI</span>
              </Link>
              
              <nav style={{ display: 'flex', gap: '1.5rem' }}>
                <Link href="/live" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  <Activity size={18} />
                  라이브 시연
                </Link>
                <Link href="/gallery" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500, color: 'var(--foreground)' }}>
                  <ImageIcon size={18} />
                  갤러리
                </Link>
                <Link href="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500, color: 'var(--foreground)' }}>
                  <LayoutDashboard size={18} />
                  성능 지표
                </Link>
              </nav>
            </div>
          </header>

          <main style={{ flex: 1, padding: '2rem 0' }}>
            {children}
          </main>

          <footer style={{ 
            borderTop: '1px solid var(--card-border)', 
            padding: '2rem 0',
            marginTop: 'auto',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.875rem'
          }}>
            <div className="container">
              <p>© 2026 Solder Void Detection Project. Phase 5 Demonstration.</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}

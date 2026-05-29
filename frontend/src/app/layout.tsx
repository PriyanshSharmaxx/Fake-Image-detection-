import './globals.css';
import React from 'react';

export const metadata = {
  title: 'DeepFake Shield - Production AI Detection Platform',
  description: 'Enterprise grade deepfake and synthetic image analysis pipeline.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col bg-[#080c14] text-slate-100">
        <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#080c14]/85 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-indigo-600/30">
                D
              </span>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                DeepFake Shield
              </span>
            </div>
            
            <nav className="flex items-center gap-6">
              <a href="/" className="text-sm font-medium text-slate-300 hover:text-white transition">
                Home
              </a>
              <a href="/dashboard" className="text-sm font-medium text-slate-300 hover:text-white transition">
                Dashboard
              </a>
              <a href="/history" className="text-sm font-medium text-slate-300 hover:text-white transition">
                History
              </a>
              <a href="/admin" className="text-sm font-medium text-slate-300 hover:text-white transition">
                Admin
              </a>
            </nav>
          </div>
        </header>

        <main className="flex-1 flex flex-col">
          {children}
        </main>

        <footer className="border-t border-slate-800 bg-slate-950 py-6 text-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} DeepFake Shield. Startup-grade Deepfake image verification network. All rights reserved.</p>
        </footer>
      </body>
    </html>
  );
}

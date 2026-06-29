"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-blue-500/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-zinc-800/50 bg-zinc-900/30 flex flex-col backdrop-blur-xl">
        <div className="h-16 flex items-center px-6 border-b border-zinc-800/50">
          <div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center border border-blue-500/20 mr-3">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <span className="font-semibold tracking-tight text-lg">CodebaseIQ</span>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          <Link href="/dashboard" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${pathname === '/dashboard' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
            Repositories
          </Link>
          <Link href="/chats" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${pathname === '/chats' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
            Chats
          </Link>
          <Link href="/settings" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${pathname === '/settings' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            Settings
          </Link>
        </nav>
        
        <div className="p-4 border-t border-zinc-800/50">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold text-zinc-300">
              ME
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">Developer</p>
              <p className="text-xs text-zinc-500 truncate">Pro Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Ambient background glow */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none" />
        
        {children}
      </main>
    </div>
  );
}

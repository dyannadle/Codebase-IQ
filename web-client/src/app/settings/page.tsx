"use client";

import React, { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [theme, setTheme] = useState("dark");
  const [fontSize, setFontSize] = useState("14");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      setApiKey(localStorage.getItem("openai_api_key") || "");
      setTheme(localStorage.getItem("theme") || "dark");
      setFontSize(localStorage.getItem("font_size") || "14");
    }
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    if (typeof window !== "undefined") {
      localStorage.setItem("openai_api_key", apiKey);
      localStorage.setItem("theme", theme);
      localStorage.setItem("font_size", fontSize);
    }
    
    setTimeout(() => {
      setIsSaving(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }, 800);
  };

  return (
    <AppLayout>
      <div className="flex-1 overflow-y-auto bg-zinc-950/80">
        <header className="h-16 flex items-center justify-between px-8 border-b border-zinc-800/50 bg-zinc-950/50 backdrop-blur-md z-10 relative">
          <h1 className="text-xl font-medium">Settings</h1>
        </header>

        <div className="max-w-3xl mx-auto p-8 relative z-10">
          <form onSubmit={handleSave} className="space-y-10">
            {/* API Keys Section */}
            <section>
              <h2 className="text-lg font-medium text-zinc-100 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
                API Configuration
              </h2>
              <div className="bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-xl p-6">
                <label className="block text-sm font-medium text-zinc-400 mb-2">OpenAI API Key</label>
                <p className="text-xs text-zinc-500 mb-4">Required for the RAG engine to generate responses.</p>
                <input 
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-3 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all font-mono"
                />
              </div>
            </section>

            {/* Appearance Section */}
            <section>
              <h2 className="text-lg font-medium text-zinc-100 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" /></svg>
                Appearance
              </h2>
              <div className="bg-zinc-900/50 backdrop-blur-sm border border-zinc-800 rounded-xl p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-3">Theme</label>
                  <div className="grid grid-cols-3 gap-4">
                    <button type="button" onClick={() => setTheme("dark")} className={`flex items-center justify-center gap-2 py-3 border rounded-lg transition-colors ${theme === 'dark' ? 'bg-blue-500/10 border-blue-500/50 text-blue-400' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
                      Dark
                    </button>
                    <button type="button" onClick={() => setTheme("light")} className={`flex items-center justify-center gap-2 py-3 border rounded-lg transition-colors ${theme === 'light' ? 'bg-blue-500/10 border-blue-500/50 text-blue-400' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                      Light
                    </button>
                    <button type="button" onClick={() => setTheme("system")} className={`flex items-center justify-center gap-2 py-3 border rounded-lg transition-colors ${theme === 'system' ? 'bg-blue-500/10 border-blue-500/50 text-blue-400' : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'}`}>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                      System
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-3">Code Editor Font Size</label>
                  <select 
                    value={fontSize}
                    onChange={(e) => setFontSize(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-3 text-zinc-100 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
                  >
                    <option value="12">12px</option>
                    <option value="14">14px (Default)</option>
                    <option value="16">16px</option>
                    <option value="18">18px</option>
                  </select>
                </div>
              </div>
            </section>

            {/* Actions */}
            <div className="flex items-center justify-between pt-6 border-t border-zinc-800/50">
              <div className="text-sm">
                {saveSuccess && (
                  <span className="text-green-400 flex items-center gap-2 animate-in fade-in slide-in-from-left-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    Settings saved successfully
                  </span>
                )}
              </div>
              <div className="flex gap-4">
                <button 
                  type="button" 
                  className="px-6 py-2 text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={isSaving}
                  className="flex items-center gap-2 px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-all shadow-[0_0_15px_rgba(59,130,246,0.2)] disabled:opacity-50"
                >
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}

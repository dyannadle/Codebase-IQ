"use client";

import React, { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";

// Define our Repository Type
interface Repository {
  id: string;
  github_repo_id: string;
  full_name: string;
  clone_url: string;
  sync_status: "QUEUED" | "CLONING" | "PARSING" | "EMBEDDING" | "ACTIVE" | "FAILED";
  last_synced_at: string | null;
}

export default function DashboardPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isFetchingRepos, setIsFetchingRepos] = useState(true);

  // Poll for repositories every 3 seconds
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        const response = await fetch("http://localhost:8001/repositories", {
          method: "GET",
          credentials: "include", // Send JWT HTTP-only cookie
        });
        if (response.ok) {
          const data = await response.json();
          setRepositories(data);
        }
      } catch (err) {
        console.error("Failed to fetch repositories:", err);
      } finally {
        setIsFetchingRepos(false);
      }
    };

    fetchRepositories();
    const intervalId = setInterval(fetchRepositories, 3000);
    return () => clearInterval(intervalId);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      // Basic github url parsing to get full_name and fake github_repo_id
      // e.g. https://github.com/tiangolo/fastapi -> tiangolo/fastapi
      const urlParts = repoUrl.replace(/\/$/, "").split("/");
      if (urlParts.length < 2) {
        throw new Error("Invalid GitHub URL");
      }
      const fullName = `${urlParts[urlParts.length - 2]}/${urlParts[urlParts.length - 1]}`;
      const repoId = `repo_${Date.now()}`; // Simulated ID

      const response = await fetch("http://localhost:8001/repositories", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Send JWT HTTP-only cookie
        body: JSON.stringify({
          github_repo_id: repoId,
          full_name: fullName,
          clone_url: repoUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to ingest repository");
      }

      setSuccessMsg("Repository queued for ingestion!");
      setTimeout(() => {
        setIsModalOpen(false);
        setRepoUrl("");
        setSuccessMsg("");
      }, 2000);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout>
        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-zinc-800/50 bg-zinc-950/50 backdrop-blur-sm z-10">
          <h1 className="text-xl font-medium">Your Repositories</h1>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:shadow-[0_0_20px_rgba(59,130,246,0.5)]"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Ingest Repository
          </button>
        </header>



        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8 relative z-10">
          {isFetchingRepos ? (
            <div className="flex items-center justify-center h-full">
              <svg className="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          ) : repositories.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center mt-[-10vh]">
              <div className="w-20 h-20 bg-zinc-900/80 rounded-2xl flex items-center justify-center mb-6 border border-zinc-800 shadow-xl">
                <svg className="w-10 h-10 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold mb-2">No Repositories Ingested</h2>
              <p className="text-zinc-400 text-sm mb-8 leading-relaxed">
                Connect a GitHub repository to begin parsing its Abstract Syntax Tree and building the structural knowledge graph for AI queries.
              </p>
              <button 
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-2 px-6 py-3 bg-zinc-100 hover:bg-white text-zinc-950 font-medium rounded-lg transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
                Connect First Repository
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {repositories.map((repo) => (
                <div key={repo.id} className="bg-zinc-900/50 backdrop-blur-sm border border-zinc-800/80 rounded-2xl p-6 flex flex-col hover:border-zinc-700 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-zinc-800 rounded-xl flex items-center justify-center border border-zinc-700">
                      <svg className="w-6 h-6 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    {/* Status Badge */}
                    <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5
                      ${repo.sync_status === 'ACTIVE' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 
                        repo.sync_status === 'FAILED' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                        'bg-blue-500/10 text-blue-400 border border-blue-500/20'}
                    `}>
                      {['QUEUED', 'CLONING', 'PARSING', 'EMBEDDING'].includes(repo.sync_status) && (
                        <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      )}
                      {repo.sync_status === 'ACTIVE' && (
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                      )}
                      {repo.sync_status}
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-zinc-100 truncate mb-1" title={repo.full_name}>
                    {repo.full_name}
                  </h3>
                  <p className="text-sm text-zinc-500 truncate mb-6" title={repo.clone_url}>
                    {repo.clone_url}
                  </p>
                  
                  <div className="mt-auto pt-4 border-t border-zinc-800/50 flex justify-between items-center text-xs text-zinc-500">
                    <span>
                      {repo.last_synced_at ? new Date(repo.last_synced_at).toLocaleDateString() : 'Never synced'}
                    </span>
                    <button className="text-zinc-400 hover:text-zinc-200 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" /></svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>


      {/* Ingestion Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-zinc-900 border border-zinc-800 w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="text-lg font-medium">Ingest Repository</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-zinc-400 hover:text-zinc-100 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-zinc-400 mb-2">GitHub Repository URL</label>
                <input 
                  type="url"
                  required
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-3 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                />
              </div>

              {errorMsg && (
                <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {errorMsg}
                </div>
              )}

              {successMsg && (
                <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm">
                  {successMsg}
                </div>
              )}

              <div className="flex justify-end gap-3 mt-8">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-zinc-100 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={isLoading}
                  className="flex items-center gap-2 px-5 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(59,130,246,0.2)]"
                >
                  {isLoading ? (
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  )}
                  {isLoading ? 'Ingesting...' : 'Start Ingestion'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}

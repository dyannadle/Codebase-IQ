"use client";

import React, { useState, useEffect, useRef } from "react";
import AppLayout from "@/components/AppLayout";
import ReactMarkdown from "react-markdown";

interface Repository {
  id: string;
  github_repo_id: string;
  full_name: string;
  clone_url: string;
  sync_status: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatsPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepoId, setSelectedRepoId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch repositories for the dropdown and poll every 5 seconds
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        const response = await fetch("http://localhost:8001/repositories", {
          method: "GET",
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          // Only allow chatting with ACTIVE repositories
          const activeRepos = data.filter((r: Repository) => r.sync_status === "ACTIVE");
          setRepositories(activeRepos);
          
          setSelectedRepoId((prev) => {
            if (activeRepos.length === 0) return "";
            if (activeRepos.some((r: Repository) => r.id === prev)) return prev;
            return activeRepos[0].id;
          });
        }
      } catch (err) {
        console.error("Failed to fetch repositories:", err);
      }
    };
    fetchRepositories();
    const intervalId = setInterval(fetchRepositories, 5000);
    return () => clearInterval(intervalId);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isStreaming || !selectedRepoId) return;

    const userQuery = inputValue;
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setIsStreaming(true);

    try {
      const response = await fetch("http://localhost:8002/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          query: userQuery,
          repository_ids: [selectedRepoId],
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to connect to chat service");
      }

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          
          // Keep the last segment (which may be incomplete) in the buffer
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") continue;
              
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                newMessages[lastIdx].content += data;
                return newMessages;
              });
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error while processing your request." },
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full bg-zinc-950/80">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-zinc-800/50 bg-zinc-950/50 backdrop-blur-md z-10 relative">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-medium">Codebase Chat</h1>
            <div className="h-4 w-px bg-zinc-800"></div>
            <select
              value={selectedRepoId}
              onChange={(e) => setSelectedRepoId(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2 outline-none"
            >
              {repositories.length === 0 ? (
                <option value="">No Active Repositories</option>
              ) : (
                repositories.map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.full_name}
                  </option>
                ))
              )}
            </select>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 relative z-10">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500">
              <div className="w-16 h-16 bg-zinc-900/50 rounded-2xl flex items-center justify-center mb-4 border border-zinc-800">
                <svg className="w-8 h-8 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <p>Ask a question about your codebase...</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div 
                  className={`max-w-3xl rounded-2xl p-5 ${
                    msg.role === "user" 
                      ? "bg-blue-600/20 border border-blue-500/30 text-blue-50" 
                      : "bg-zinc-900/80 border border-zinc-800 text-zinc-300 backdrop-blur-sm shadow-xl"
                  }`}
                >
                  <div className="prose prose-invert prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800 max-w-none text-sm md:text-base leading-relaxed">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-8 border-t border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl z-10 relative">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl blur opacity-10 group-focus-within:opacity-30 transition duration-500"></div>
            <div className="relative flex items-center bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={selectedRepoId ? "Ask how a specific component works..." : "Please select an active repository first..."}
                disabled={!selectedRepoId || isStreaming}
                className="w-full bg-transparent border-none px-6 py-4 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-0 disabled:opacity-50"
              />
              <button 
                type="submit" 
                disabled={!inputValue.trim() || isStreaming || !selectedRepoId}
                className="mr-3 p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:bg-zinc-800 disabled:text-zinc-500 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}



export default function LoginPage() {
  return (
    <main className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-4">
      {/* Background ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Main Login Card */}
      <div className="relative z-10 w-full max-w-md p-8 bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/50 rounded-2xl shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-zinc-800 rounded-xl flex items-center justify-center mb-4 border border-zinc-700">
            <svg
              className="w-8 h-8 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">
            CodebaseIQ
          </h1>
          <p className="text-zinc-400 mt-2 text-sm text-center">
            Sign in to access your repository intelligence dashboard.
          </p>
        </div>

        <div className="space-y-4">
          <a
            href="http://localhost:8000/auth/github/login"
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-all duration-200 shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)]"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
            Continue with GitHub
          </a>
          
          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-zinc-800"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-zinc-900/60 px-2 text-zinc-500">Secure Enterprise Access</span>
            </div>
          </div>
        </div>

        <p className="mt-8 text-center text-xs text-zinc-500">
          By clicking continue, you agree to our{" "}
          <a href="#" className="underline hover:text-zinc-300">Terms of Service</a>{" "}
          and{" "}
          <a href="#" className="underline hover:text-zinc-300">Privacy Policy</a>.
        </p>
      </div>
    </main>
  );
}

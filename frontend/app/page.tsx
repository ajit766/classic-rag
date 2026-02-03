import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-purple-900/30 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-blue-900/30 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2" />

      {/* Main Content */}
      <main className="z-10 text-center px-4 max-w-4xl mx-auto space-y-8">

        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-sm font-medium text-gray-300">Advanced RAG V2 Active</span>
        </div>

        {/* Hero Text */}
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
          The Modern Sage
        </h1>

        <p className="text-xl md:text-2xl text-gray-400 font-light max-w-2xl mx-auto leading-relaxed">
          Where <span className="text-blue-400 font-medium">Modern Psychology</span> meets{" "}
          <span className="text-purple-400 font-medium">Ancient Wisdom</span>.
        </p>

        <p className="text-base text-gray-500 max-w-lg mx-auto">
          A dual-perspective AI guided by behavioral psychology and timeless philosophy.
          Grounded in truth, backed by citations.
        </p>

        {/* CTA Button */}
        <div className="pt-8">
          <Link
            href="/chat"
            className="group relative inline-flex items-center justify-center px-8 py-3 text-lg font-medium text-white bg-white/10 border border-white/10 rounded-full overflow-hidden transition-all duration-300 hover:bg-white/20 hover:scale-105 hover:shadow-[0_0_20px_rgba(255,255,255,0.2)]"
          >
            <span className="relative z-10 flex items-center gap-2">
              Start Consultation
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="absolute bottom-8 text-center px-4">
        <p className="text-gray-400 text-sm font-medium tracking-wide">
          Synthesizing insights from <span className="text-gray-300">Atomic Habits</span>, <span className="text-gray-300">Ikigai</span>, <span className="text-gray-300">The 7 Habits of Highly Effective People</span>, and <span className="text-gray-300">The Bhagavad Gita</span>.
        </p>
      </footer>
    </div>
  );
}

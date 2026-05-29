import React from 'react';

export default function Home() {
  return (
    <div className="relative overflow-hidden flex-1 flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-20 bg-radial-gradient">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/20 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-96 h-96 bg-cyan-600/20 rounded-full blur-[128px] pointer-events-none" />

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/5 text-xs text-indigo-400 mb-8 font-medium animate-pulse">
          🛡️ Startup-Grade Image Analysis & Verification
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-6 leading-none">
          Identify synthetic and manipulated images with{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
            Explainable AI
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload any photo to verify authenticity. DeepFake Shield deploys dual-path spatial ConvNeXts and 2D-DCT frequency networks to pinpoint diffusion, GAN, and digital splicing signatures.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a
            href="/dashboard"
            className="w-full sm:w-auto h-12 px-8 flex items-center justify-center rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white transition-all duration-200 shadow-lg shadow-indigo-600/30 hover:scale-[1.02]"
          >
            Launch Analyzer
          </a>
          <a
            href="/admin"
            className="w-full sm:w-auto h-12 px-8 flex items-center justify-center rounded-xl border border-slate-700 bg-slate-900/50 hover:bg-slate-900 text-sm font-semibold text-slate-300 hover:text-white transition-all duration-200"
          >
            Developer Dashboard
          </a>
        </div>
      </div>

      {/* Feature cards Grid */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 relative z-10 w-full">
        {/* Card 1 */}
        <div className="glass p-6 rounded-2xl flex flex-col gap-4">
          <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 font-bold">
            01
          </div>
          <h3 className="text-lg font-bold text-slate-200">Dual-Path Ensembles</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Combines spatial model evaluation with 2D Discrete Cosine Transform spectral analysis to expose frequency grid patterns left behind by upsampling layers.
          </p>
        </div>

        {/* Card 2 */}
        <div className="glass p-6 rounded-2xl flex flex-col gap-4">
          <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 font-bold">
            02
          </div>
          <h3 className="text-lg font-bold text-slate-200">Grad-CAM Heatmaps</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            See what the model sees. Visual heatmaps highlight the specific pixel blending boundaries and artifact sectors that drove the classification.
          </p>
        </div>

        {/* Card 3 */}
        <div className="glass p-6 rounded-2xl flex flex-col gap-4">
          <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 font-bold">
            03
          </div>
          <h3 className="text-lg font-bold text-slate-200">API Access</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Deploy check-points straight to your ingestion pipeline using developer keys. Seamless integration with external automation tools.
          </p>
        </div>
      </div>
    </div>
  );
}

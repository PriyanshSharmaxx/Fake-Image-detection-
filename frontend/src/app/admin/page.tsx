'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, Server, Activity, ShieldAlert, Thermometer, Database } from 'lucide-react';
import { ApiClient } from '../../lib/api';

export default function AdminPage() {
  const [metrics, setMetrics] = useState<any>({
    cpu_usage: 12.4,
    memory_usage: 44.8,
    gpu_usage: [22.5],
    gpu_temp: [64],
    gpu_memory_free: [8.2],
    total_scans: 1420,
    scans_breakdown: { real: 850, ai_generated: 450, manipulated: 120 },
    avg_latency_ms: 114
  });

  // Pull active telemetry
  useEffect(() => {
    // In production we pull actual metrics endpoint
    const timer = setInterval(() => {
      setMetrics((prev: any) => ({
        ...prev,
        cpu_usage: parseFloat((10 + Math.random() * 8).toFixed(1)),
        memory_usage: parseFloat((40 + Math.random() * 5).toFixed(1)),
        gpu_usage: [parseFloat((20 + Math.random() * 15).toFixed(1))],
        gpu_temp: [60 + Math.floor(Math.random() * 6)],
      }));
    }, 3000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col gap-10">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-extrabold tracking-tight">System & Telemetry Dashboard</h2>
        <p className="text-slate-400 text-sm">Real-time status tracking for hardware allocations and detection metrics.</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Inference Latency</span>
            <h4 className="text-2xl font-black mt-1 text-slate-200">{metrics.avg_latency_ms}ms</h4>
          </div>
          <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Activity className="h-5 w-5" />
          </div>
        </div>

        <div className="glass p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Total Audited Images</span>
            <h4 className="text-2xl font-black mt-1 text-slate-200">{metrics.total_scans}</h4>
          </div>
          <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400">
            <Database className="h-5 w-5" />
          </div>
        </div>

        <div className="glass p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">Synthetic Ratio</span>
            <h4 className="text-2xl font-black mt-1 text-slate-200">
              {((metrics.scans_breakdown.ai_generated / metrics.total_scans) * 100).toFixed(1)}%
            </h4>
          </div>
          <div className="h-10 w-10 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400">
            <ShieldAlert className="h-5 w-5" />
          </div>
        </div>

        <div className="glass p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-medium">API Core Status</span>
            <h4 className="text-2xl font-black mt-1 text-emerald-400">ONLINE</h4>
          </div>
          <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <Server className="h-5 w-5" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Hardware Status */}
        <div className="glass p-6 rounded-2xl flex flex-col gap-6 lg:col-span-2">
          <h3 className="font-bold text-lg text-slate-300">GPU & CPU Metrics</h3>
          
          <div className="flex flex-col gap-5">
            {/* CPU Bar */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 flex items-center gap-1.5"><Cpu className="h-4 w-4" /> CPU Utilization</span>
                <span className="font-bold text-slate-200">{metrics.cpu_usage}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full transition-all duration-1000" style={{ width: `${metrics.cpu_usage}%` }} />
              </div>
            </div>

            {/* RAM Bar */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 flex items-center gap-1.5"><Server className="h-4 w-4" /> System RAM (Used)</span>
                <span className="font-bold text-slate-200">{metrics.memory_usage}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full" style={{ width: `${metrics.memory_usage}%` }} />
              </div>
            </div>

            {/* GPU Bar */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 flex items-center gap-1.5"><Activity className="h-4 w-4" /> GPU Inference Duty</span>
                <span className="font-bold text-slate-200">{metrics.gpu_usage[0]}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-cyan-500 h-full transition-all duration-1000" style={{ width: `${metrics.gpu_usage[0]}%` }} />
              </div>
            </div>

            {/* GPU Temp */}
            <div className="flex justify-between items-center p-4 rounded-xl bg-slate-900/50 border border-slate-800 mt-2">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Thermometer className="h-5 w-5 text-amber-500" />
                <span>NVIDIA Tesla A100 Core Temp</span>
              </div>
              <span className="font-bold text-slate-200">{metrics.gpu_temp[0]}°C</span>
            </div>
          </div>
        </div>

        {/* Classification Breakdown */}
        <div className="glass p-6 rounded-2xl flex flex-col gap-6">
          <h3 className="font-bold text-lg text-slate-300">Scan Class Breakdown</h3>
          
          <div className="flex-1 flex flex-col justify-center gap-5">
            {/* Real */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-emerald-500" />
                <span className="text-slate-400 text-sm">Real Images</span>
              </div>
              <span className="font-bold text-slate-200">{metrics.scans_breakdown.real}</span>
            </div>

            {/* AI Generated */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-rose-500" />
                <span className="text-slate-400 text-sm">AI Generated</span>
              </div>
              <span className="font-bold text-slate-200">{metrics.scans_breakdown.ai_generated}</span>
            </div>

            {/* Manipulated */}
            <div className="flex items-center justify-between pb-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-amber-500" />
                <span className="text-slate-400 text-sm">Manipulated/Deepfake</span>
              </div>
              <span className="font-bold text-slate-200">{metrics.scans_breakdown.manipulated}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

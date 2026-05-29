'use client';

import React, { useEffect, useState } from 'react';
import { ApiClient } from '../../lib/api';
import { History, ShieldAlert, ShieldCheck, Eye, Trash2 } from 'lucide-react';

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await ApiClient.request('/detections/history');
        setHistory(data);
      } catch (err: any) {
        setError(err.message || 'Failed to retrieve logs.');
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  const getResultTag = (res: string) => {
    if (res === 'real') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <ShieldCheck className="h-3 w-3" /> Real
        </span>
      );
    }
    if (res === 'ai_generated') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <ShieldAlert className="h-3 w-3" /> Synthetic
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
        <ShieldAlert className="h-3 w-3" /> Manipulated
      </span>
    );
  };

  const getS3Url = (key: string) => {
    const endpoint = 'http://localhost:9000/uploads/';
    return `${endpoint}${key}`;
  };

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col gap-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-extrabold tracking-tight">Audit Log & History</h2>
        <p className="text-slate-400 text-sm">Review past verification pipeline uploads and classifications.</p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-sm">
          {error}
        </div>
      ) : history.length === 0 ? (
        <div className="border border-slate-800 bg-slate-950/20 rounded-2xl p-16 text-center flex flex-col items-center justify-center gap-4 text-slate-500">
          <History className="h-10 w-10 text-slate-700" />
          <div>
            <p className="font-semibold text-slate-400">No detection history</p>
            <p className="text-xs text-slate-600 mt-1">Images you analyze in the dashboard will appear here.</p>
          </div>
        </div>
      ) : (
        <div className="glass rounded-2xl overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/50 text-slate-400 text-xs font-bold uppercase tracking-wider">
                  <th className="py-4 px-6">Image</th>
                  <th className="py-4 px-6">Result</th>
                  <th className="py-4 px-6">Confidence</th>
                  <th className="py-4 px-6">Latency</th>
                  <th className="py-4 px-6">Timestamp</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-sm">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/20 transition">
                    <td className="py-4 px-6">
                      <div className="h-12 w-12 rounded-lg overflow-hidden border border-slate-800 bg-slate-950 flex items-center justify-center">
                        <img
                          src={getS3Url(item.img_s3_url)}
                          alt="Scan Thumbnail"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </td>
                    <td className="py-4 px-6">{getResultTag(item.result)}</td>
                    <td className="py-4 px-6 font-semibold text-slate-200">
                      {parseFloat(item.confidence).toFixed(2)}%
                    </td>
                    <td className="py-4 px-6 text-slate-400">{item.latency_ms}ms</td>
                    <td className="py-4 px-6 text-slate-400">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="inline-flex gap-2">
                        <a
                          href={`/dashboard?id=${item.id}`}
                          className="h-9 w-9 rounded-lg border border-slate-700 bg-slate-900 flex items-center justify-center text-slate-400 hover:text-white transition"
                        >
                          <Eye className="h-4 w-4" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

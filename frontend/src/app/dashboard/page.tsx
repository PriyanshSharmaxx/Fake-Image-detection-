'use client';

import React, { useState, useRef } from 'react';
import { Upload, HelpCircle, ShieldAlert, ShieldCheck, Cpu, RefreshCw, Layers } from 'lucide-react';
import { ApiClient } from '../../lib/api';

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [sliderPos, setSliderPos] = useState(50); // percentage for heatmap swipe overlay

  const fileInputRef = useRef<HTMLInputElement>(null);
  const sliderContainerRef = useRef<HTMLDivElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(10);
    setError(null);

    try {
      // Simulate file upload progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => (prev < 90 ? prev + 15 : prev));
      }, 300);

      const data = await ApiClient.uploadAndAnalyze(file, () => {
        clearInterval(progressInterval);
        setProgress(100);
      });

      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Verification pipeline encountered a failure.');
    } finally {
      setUploading(false);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!sliderContainerRef.current) return;
    const rect = sliderContainerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(percentage);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!sliderContainerRef.current || !e.touches[0]) return;
    const rect = sliderContainerRef.current.getBoundingClientRect();
    const x = e.touches[0].clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(percentage);
  };

  const resetUploader = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const getResultColor = (res: string) => {
    if (res === 'real') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (res === 'ai_generated') return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
    return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
  };

  // Convert raw relative S3 path to local/MinIO url helper
  const getS3Url = (key: string) => {
    const endpoint = 'http://localhost:9000/uploads/';
    return `${endpoint}${key}`;
  };

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col gap-10">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-extrabold tracking-tight">Image Integrity Analyzer</h2>
        <p className="text-slate-400 text-sm">Upload images to test spatial and spectral artifacts.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Left Side: Upload Zone */}
        <div className="flex flex-col gap-6">
          {!previewUrl ? (
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 bg-slate-900/30 hover:bg-slate-900/50 rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-4 cursor-pointer transition duration-200 min-h-[350px] relative overflow-hidden"
            >
              <div className="h-12 w-12 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <Upload className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-slate-200">Drag & drop your image here</p>
                <p className="text-xs text-slate-500 mt-1">Supports PNG, JPG, or WEBP (Max 10MB)</p>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
              />
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <div className="relative border border-slate-800 bg-slate-950 rounded-2xl overflow-hidden aspect-video flex items-center justify-center min-h-[350px]">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-[350px] w-auto object-contain"
                />
                
                {/* Laser scan line overlay during uploading */}
                {uploading && (
                  <div className="absolute left-0 w-full h-1 bg-indigo-500 shadow-[0_0_15px_#6366f1] animate-scan" />
                )}
              </div>

              {uploading && (
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-indigo-500 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}

              <div className="flex gap-4">
                {!uploading && !result && (
                  <button
                    onClick={handleAnalyze}
                    className="flex-1 h-12 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold transition"
                  >
                    Run Classification
                  </button>
                )}
                
                <button
                  onClick={resetUploader}
                  disabled={uploading}
                  className="px-6 h-12 border border-slate-700 bg-slate-900 text-slate-300 rounded-xl font-semibold hover:bg-slate-800 transition disabled:opacity-50"
                >
                  Clear
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-sm flex gap-2 items-center">
              <ShieldAlert className="h-5 w-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right Side: Results Display */}
        <div className="flex flex-col gap-6">
          {!result ? (
            <div className="border border-slate-800 bg-slate-950/20 rounded-2xl p-10 flex flex-col items-center justify-center text-center gap-4 text-slate-500 min-h-[400px]">
              <HelpCircle className="h-10 w-10 text-slate-700" />
              <div>
                <p className="font-semibold text-slate-400">Waiting for classification</p>
                <p className="text-xs text-slate-600 mt-1">Upload an image and run verification to display indicators.</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-6 animate-fade-in">
              {/* Classification Tag */}
              <div className={`p-5 rounded-2xl border flex items-center justify-between ${getResultColor(result.result)}`}>
                <div className="flex items-center gap-3">
                  {result.result === 'real' ? (
                    <ShieldCheck className="h-8 w-8" />
                  ) : (
                    <ShieldAlert className="h-8 w-8" />
                  )}
                  <div>
                    <h3 className="font-bold text-lg uppercase tracking-wider">{result.result.replace('_', ' ')}</h3>
                    <p className="text-xs opacity-80">Final fusion prediction classification</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-extrabold">{parseFloat(result.confidence).toFixed(2)}%</span>
                  <p className="text-[10px] uppercase opacity-75">Confidence Score</p>
                </div>
              </div>

              {/* Spatial vs Frequency distribution */}
              <div className="grid grid-cols-2 gap-4">
                <div className="glass p-5 rounded-2xl flex flex-col gap-2">
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span>Spatial Path</span>
                    <Cpu className="h-4 w-4 text-indigo-400" />
                  </div>
                  <span className="text-xl font-bold text-slate-200">
                    {(parseFloat(result.spatial_score) * 100).toFixed(2)}%
                  </span>
                  <p className="text-[10px] text-slate-500">Local texture evaluation</p>
                </div>

                <div className="glass p-5 rounded-2xl flex flex-col gap-2">
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span>Frequency Path</span>
                    <Layers className="h-4 w-4 text-cyan-400" />
                  </div>
                  <span className="text-xl font-bold text-slate-200">
                    {(parseFloat(result.freq_score) * 100).toFixed(2)}%
                  </span>
                  <p className="text-[10px] text-slate-500">2D DCT periodic assessment</p>
                </div>
              </div>

              {/* Grad-CAM Heatmap Swiper */}
              {result.heatmap_s3_url && (
                <div className="flex flex-col gap-3">
                  <h4 className="font-bold text-sm text-slate-300">Grad-CAM Feature Activation Map</h4>
                  
                  <div 
                    ref={sliderContainerRef}
                    onMouseMove={handleMouseMove}
                    onTouchMove={handleTouchMove}
                    className="relative w-full aspect-video rounded-2xl overflow-hidden cursor-ew-resize border border-slate-800 select-none bg-slate-950"
                  >
                    {/* Layer 1: Heatmap (Underneath / Right side) */}
                    <img 
                      src={getS3Url(result.heatmap_s3_url)} 
                      alt="Heatmap" 
                      className="absolute inset-0 w-full h-full object-contain pointer-events-none"
                    />
                    
                    {/* Layer 2: Original Image (Overlayed on Left side) */}
                    <div 
                      className="absolute inset-0 overflow-hidden pointer-events-none"
                      style={{ clipPath: `polygon(0 0, ${sliderPos}% 0, ${sliderPos}% 100%, 0 100%)` }}
                    >
                      <img 
                        src={previewUrl!} 
                        alt="Original" 
                        className="w-full h-full object-contain pointer-events-none"
                      />
                    </div>

                    {/* Divider line bar */}
                    <div 
                      className="absolute top-0 bottom-0 w-0.5 bg-indigo-500 shadow-[0_0_10px_#6366f1] pointer-events-none"
                      style={{ left: `${sliderPos}%` }}
                    >
                      <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-8 w-8 rounded-full bg-indigo-600 border-2 border-indigo-400 flex items-center justify-center shadow-lg">
                        <RefreshCw className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  </div>
                  <p className="text-center text-[10px] text-slate-500">Move cursor across image to toggle heatmap transparency</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

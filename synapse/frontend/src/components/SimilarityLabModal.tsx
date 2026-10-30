import React, { useState } from 'react';
import { 
  X, 
  Layers, 
  BarChart3, 
  Share2, 
  Info, 
  Compass, 
  Maximize2, 
  Hash, 
  FileText
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ScatterChart, 
  Scatter, 
  ZAxis, 
  Cell 
} from 'recharts';
import { AnalysisResult, Chunk } from '../types';

interface SimilarityLabModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: AnalysisResult | null;
  onLocateInViewer: (chunk: Chunk) => void;
}

export const SimilarityLabModal: React.FC<SimilarityLabModalProps> = ({
  isOpen,
  onClose,
  analysis,
  onLocateInViewer
}) => {
  const [activeTab, setActiveTab] = useState<'barchart' | 'projection' | 'math'>('barchart');
  const [selectedPoint, setSelectedPoint] = useState<any>(null);

  if (!isOpen || !analysis) return null;

  // Prepare data for horizontal bar chart
  const barChartData = analysis.ranked_chunks.map((c) => ({
    name: `Passage #${c.index + 1} (P.${c.page})`,
    shortName: `P#${c.index + 1}`,
    score: Number((c.score! * 100).toFixed(1)),
    text: c.text,
    rawScore: c.score,
    page: c.page,
    chunk: c
  }));

  // Prepare scatter plot data from PCA projection
  const queryPoint = analysis.projection_2d.points.find(p => p.type === 'query');
  const chunkPoints = analysis.projection_2d.points.filter(p => p.type === 'chunk');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[88vh] rounded-2xl bg-background-card border border-surface-border shadow-premium flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface-50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan/10 border border-cyan/20">
              <Layers className="w-5 h-5 text-cyan" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Semantic Similarity Lab
                </h2>
                <span className="px-2 py-0.5 rounded bg-surface-200 text-cyan text-[10px] font-mono font-medium">
                  128D Multi-Dimensional Space
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Mathematical vector inspection, PCA dimensionality reduction, and passage leaderboard.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* View Switcher Tabs */}
            <div className="flex p-1 rounded-lg bg-surface-100 border border-surface-border text-xs font-mono">
              <button
                onClick={() => setActiveTab('barchart')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                  activeTab === 'barchart'
                    ? 'bg-surface-200 text-cyan shadow-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <BarChart3 className="w-3.5 h-3.5" />
                <span>Rankings</span>
              </button>
              <button
                onClick={() => setActiveTab('projection')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                  activeTab === 'projection'
                    ? 'bg-surface-200 text-cyan shadow-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Compass className="w-3.5 h-3.5" />
                <span>2D Vector Space</span>
              </button>
              <button
                onClick={() => setActiveTab('math')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                  activeTab === 'math'
                    ? 'bg-surface-200 text-cyan shadow-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Info className="w-3.5 h-3.5" />
                <span>Formula & Audit</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-surface-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* TAB 1: BARCHART LEADERBOARD */}
          {activeTab === 'barchart' && (
            <div className="space-y-6">
              
              {/* Leaderboard Chart Card */}
              <div className="p-5 rounded-xl bg-surface-50 border border-surface-border">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-100">
                      Top Retrieved Passages by Cosine Similarity Metric
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Query: "{analysis.query}"
                    </p>
                  </div>
                  <span className="text-xs font-mono text-cyan bg-cyan/10 px-2.5 py-1 rounded border border-cyan/20">
                    Highest Match: {analysis.top_score_percentage}
                  </span>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={barChartData}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                    >
                      <XAxis 
                        type="number" 
                        domain={[0, 100]} 
                        stroke="#64748b" 
                        tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                        unit="%"
                      />
                      <YAxis 
                        dataKey="shortName" 
                        type="category" 
                        stroke="#64748b" 
                        tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="p-3 rounded-lg bg-surface-200 border border-surface-border text-xs text-slate-200 shadow-premium max-w-sm">
                                <div className="font-mono text-cyan font-semibold mb-1">
                                  {data.name} — {data.score}% Match
                                </div>
                                <p className="text-[11px] text-slate-300 line-clamp-3">
                                  "{data.text}"
                                </p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                        {barChartData.map((_, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={index === 0 ? '#06b6d4' : '#6366f1'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Detailed Passages Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.ranked_chunks.map((chunk, idx) => (
                  <div 
                    key={chunk.index}
                    className="p-4 rounded-xl bg-surface-50 border border-surface-border space-y-2 hover:border-cyan/40 transition-all text-left"
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-cyan font-bold flex items-center gap-1.5">
                        <Hash className="w-3.5 h-3.5" />
                        Rank #{idx + 1} — Passage #{chunk.index + 1}
                      </span>
                      <span className="text-emerald-400 font-semibold">
                        {(chunk.score! * 100).toFixed(1)}% Match (Page {chunk.page})
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      "{chunk.text}"
                    </p>

                    <div className="pt-2 border-t border-surface-border flex items-center justify-between text-[11px] font-mono text-slate-400">
                      <span>{chunk.wordCount} words</span>
                      <button
                        onClick={() => {
                          onClose();
                          onLocateInViewer(chunk);
                        }}
                        className="text-cyan hover:underline flex items-center gap-1"
                      >
                        <FileText className="w-3 h-3" />
                        <span>Inspect in Document Viewer</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

            </div>
          )}

          {/* TAB 2: 2D VECTOR SPACE PROJECTION (PCA) */}
          {activeTab === 'projection' && (
            <div className="space-y-6">
              
              <div className="p-5 rounded-xl bg-surface-50 border border-surface-border space-y-4">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                      <Compass className="w-4 h-4 text-cyan" />
                      2D Vector Space Projection (PCA)
                    </h3>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">
                      Authentic dimensionality reduction of 128D semantic unit vectors.
                    </p>
                  </div>
                  {analysis.projection_2d.variance_explained && (
                    <div className="text-xs font-mono text-slate-400 bg-surface-100 px-3 py-1 rounded border border-surface-border">
                      Variance Explained: PC1={((analysis.projection_2d.variance_explained[0] || 0) * 100).toFixed(1)}%, PC2={((analysis.projection_2d.variance_explained[1] || 0) * 100).toFixed(1)}%
                    </div>
                  )}
                </div>

                <div className="h-80 w-full bg-surface-100/50 rounded-lg p-2 border border-surface-border/60">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <XAxis 
                        type="number" 
                        dataKey="x" 
                        domain={[-100, 100]} 
                        stroke="#475569" 
                        tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }}
                        name="Principal Component 1"
                      />
                      <YAxis 
                        type="number" 
                        dataKey="y" 
                        domain={[-100, 100]} 
                        stroke="#475569" 
                        tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }}
                        name="Principal Component 2"
                      />
                      <ZAxis range={[60, 160]} />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const pt = payload[0].payload;
                            return (
                              <div className="p-3 rounded-lg bg-surface-200 border border-cyan/40 text-xs text-slate-200 shadow-premium max-w-xs">
                                <div className="font-mono text-cyan font-bold mb-1">
                                  {pt.label}
                                </div>
                                <div className="text-[10px] font-mono text-slate-400 mb-1">
                                  PCA Coordinates: ({pt.x}, {pt.y})
                                </div>
                                <p className="text-[11px] text-slate-300">
                                  "{pt.preview}"
                                </p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      {/* Query point */}
                      {queryPoint && (
                        <Scatter 
                          name="Query" 
                          data={[queryPoint]} 
                          fill="#06b6d4" 
                          shape="cross"
                        />
                      )}
                      {/* Document chunks */}
                      <Scatter 
                        name="Passages" 
                        data={chunkPoints} 
                        fill="#6366f1"
                        onClick={(e) => setSelectedPoint(e)}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-2">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 bg-cyan inline-block rounded-sm" />
                      User Query Vector
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 bg-indigo inline-block rounded-full" />
                      Document Passage Chunks
                    </span>
                  </div>
                  <span>Proximity in 2D reflects high cosine similarity in 128D</span>
                </div>
              </div>

            </div>
          )}

          {/* TAB 3: FORMULA & MATHEMATICAL AUDIT */}
          {activeTab === 'math' && (
            <div className="space-y-6">
              
              <div className="p-5 rounded-xl bg-surface-50 border border-surface-border space-y-4 text-left">
                <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                  <Info className="w-4 h-4 text-cyan" />
                  Mathematical Vector Engine Specification
                </h3>

                <div className="p-4 rounded-lg bg-surface-100 font-mono text-xs text-cyan space-y-3 border border-surface-border">
                  <div>
                    <span className="text-slate-400 block mb-1">1. Geometric Cosine Similarity Formulation:</span>
                    <p className="text-sm">cos(θ) = (q · c) / (||q|| · ||c||) = Σ(q_i · c_i)</p>
                  </div>

                  <div>
                    <span className="text-slate-400 block mb-1">2. Dual FNV-1a & DJB2 Hash Mixing:</span>
                    <p>h1 = ((h1 ^ char) * 16777619) & 0xFFFFFFFF</p>
                    <p>h2 = (((h2 &lt;&lt; 5) + h2) ^ char) & 0xFFFFFFFF</p>
                  </div>

                  <div>
                    <span className="text-slate-400 block mb-1">3. L2 Unit Normalization:</span>
                    <p>||v|| = sqrt(Σ v_i^2) = 1.0000</p>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-300 leading-relaxed">
                  <p>
                    <strong>Algorithmic Integrity:</strong> Synapse operationalizes the exact pure Python similarity engine without relying on black-box external vector APIs. Dense 128-dimensional continuous representations are deterministically computed using:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-slate-400 pl-2">
                    <li>TF-IDF word length salience weighting (downweighting common grammatical stop words).</li>
                    <li>Dual 32-bit FNV-1a and DJB2 hash mixing seeds for high-entropy dimension dispersal.</li>
                    <li>Subword character 3-gram hashing for morphological resilience against typos or pluralizations.</li>
                    <li>Strict L2 unit normalization ensuring exact spherical cosine dot-product comparisons.</li>
                  </ul>
                </div>
              </div>

            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-surface-border bg-surface-50 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Engine: Synapse 128D Deterministic Hash Architecture</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-surface-100 hover:bg-surface-200 text-slate-200 border border-surface-border transition-colors"
          >
            Close Lab
          </button>
        </div>

      </div>
    </div>
  );
};

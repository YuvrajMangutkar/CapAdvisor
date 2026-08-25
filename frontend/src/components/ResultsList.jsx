import { useState } from 'react';
import { getExcelUrl, getPdfUrl } from '../api';
import CollegeCard from './CollegeCard';

export default function ResultsList({ data, searchParams, onTriggerFeedback }) {
  const [downloadNotice, setDownloadNotice] = useState(false);

  if (!data) return null;

  const handleDownloadClick = () => {
    setDownloadNotice(true);
  };

  const {
    student_percentile,
    category_code,
    reach_count,
    match_count,
    safe_count,
    explore_count,
    entries,
  } = data;

  if (entries.length === 0) {
    return (
      <div className="glass-panel p-12 text-center mt-12">
        <div className="text-4xl mb-4">🔍</div>
        <h3 className="text-lg font-bold text-white mb-2">No colleges matched your filters.</h3>
        <p className="text-sm text-slate-400">Try expanding your location or branch preferences.</p>
      </div>
    );
  }

  const reaches = entries.filter(e => e.classification === 'Reach');
  const matches = entries.filter(e => e.classification === 'Match');
  const safes   = entries.filter(e => e.classification === 'Safe');

  return (
    <div className="mt-12 w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h2 className="text-xl md:text-2xl font-black text-white tracking-tight">Your CAP Preference List</h2>
          <p className="text-xs text-slate-400 mt-1">
            Percentile: <span className="font-bold text-indigo-400">{student_percentile}</span> | Category: <span className="font-bold text-purple-400">{category_code}</span>
          </p>
        </div>
        <div className="flex gap-2">
          {reach_count > 0 && (
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400">
              {reach_count} Reach
            </span>
          )}
          {match_count > 0 && (
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              {match_count} Match
            </span>
          )}
          {safe_count > 0  && (
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400">
              {safe_count} Safe
            </span>
          )}
          {explore_count > 0 && (
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-500/10 border border-slate-500/30 text-slate-300">
              {explore_count} Explore
            </span>
          )}
        </div>
      </div>

      {/* ── Reach ── */}
      {reaches.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-wider text-amber-450 mb-3">
            <span>Reach Options (Target High)</span>
            <div className="h-px flex-1 bg-amber-500/20" />
          </div>
          <div className="flex flex-col">
            {reaches.map((e, i) => (
              <CollegeCard key={e.rank} entry={e} style={{ animationDelay: `${i * 0.05}s` }} />
            ))}
          </div>
        </div>
      )}

      {/* ── Match ── */}
      {matches.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3">
            <span>Match Options (Balanced Choice)</span>
            <div className="h-px flex-1 bg-emerald-500/20" />
          </div>
          <div className="flex flex-col">
            {matches.map((e, i) => (
              <CollegeCard key={e.rank} entry={e} style={{ animationDelay: `${(reaches.length + i) * 0.05}s` }} />
            ))}
          </div>
        </div>
      )}

      {/* ── Safe ── */}
      {safes.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-wider text-blue-400 mb-3">
            <span>Safe Options (Solid Backups)</span>
            <div className="h-px flex-1 bg-blue-500/20" />
          </div>
          <div className="flex flex-col">
            {safes.map((e, i) => (
              <CollegeCard key={e.rank} entry={e} style={{ animationDelay: `${(reaches.length + matches.length + i) * 0.05}s` }} />
            ))}
          </div>
        </div>
      )}

      {entries.filter(e => e.classification === 'Explore').length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
            <span>Explore Options (late-round possibility)</span>
            <div className="h-px flex-1 bg-slate-500/20" />
          </div>
          <div className="flex flex-col">
            {entries.filter(e => e.classification === 'Explore').map((e, i) => (
              <CollegeCard key={e.rank} entry={e} style={{ animationDelay: `${(reaches.length + matches.length + safes.length + i) * 0.05}s` }} />
            ))}
          </div>
        </div>
      )}

      {/* ── Export Bar ── */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl mt-8">
        <div className="text-sm font-semibold text-slate-300">Ready to fill your official CAP application?</div>
        <div className="flex gap-3 w-full sm:w-auto">
          <a
            id="export-excel-btn"
            href={getExcelUrl(searchParams)}
            onClick={handleDownloadClick}
            className="flex-1 sm:flex-none text-center text-xs font-bold px-4 py-2.5 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:border-indigo-500 hover:text-indigo-400 transition-all duration-150 cursor-pointer"
            download
          >
            📊 Download Excel
          </a>
          <a
            id="export-pdf-btn"
            href={getPdfUrl(searchParams)}
            onClick={handleDownloadClick}
            className="flex-1 sm:flex-none text-center text-xs font-bold px-4 py-2.5 rounded-xl border border-slate-800 bg-slate-900 text-slate-300 hover:border-purple-500 hover:text-purple-400 transition-all duration-150 cursor-pointer"
            download
          >
            📄 Download PDF
          </a>
        </div>
      </div>

      {downloadNotice && (
        <div className="mt-4 p-4 rounded-2xl bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg">
          <span>🎉 <strong>Download Started!</strong> How was your experience generating your list? Tell us if you faced any issues.</span>
          <button
            type="button"
            onClick={() => onTriggerFeedback && onTriggerFeedback(true)}
            className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs transition-all active:scale-95 shrink-0 cursor-pointer shadow-sm"
          >
            Share Experience & Feedback 💬
          </button>
        </div>
      )}
    </div>
  );
}

// src/components/CollegeCard.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, MapPin, Award } from 'lucide-react';

export default function CollegeCard({ entry, style }) {
  const [expanded, setExpanded] = useState(false);
  const { classification: tier } = entry;

  // Custom colors for Reach/Match/Safe using tailwind gradient combos
  const colorMap = {
    Reach: {
      bg: 'from-amber-500/10 to-orange-500/10 border-amber-500/30 text-amber-300',
      badge: 'bg-amber-500 text-slate-950',
      hover: 'hover:border-amber-400/60 shadow-amber-500/5',
      rankBg: 'bg-amber-500/20 text-amber-300'
    },
    Match: {
      bg: 'from-emerald-500/10 to-teal-500/10 border-emerald-500/30 text-emerald-300',
      badge: 'bg-emerald-500 text-slate-950',
      hover: 'hover:border-emerald-400/60 shadow-emerald-500/5',
      rankBg: 'bg-emerald-500/20 text-emerald-300'
    },
    Safe: {
      bg: 'from-blue-500/10 to-indigo-500/10 border-blue-500/30 text-blue-300',
      badge: 'bg-blue-500 text-slate-950',
      hover: 'hover:border-blue-400/60 shadow-blue-500/5',
      rankBg: 'bg-blue-500/20 text-blue-300'
    },
    Explore: {
      bg: 'from-slate-500/10 to-cyan-500/10 border-slate-500/30 text-slate-300',
      badge: 'bg-slate-400 text-slate-950',
      hover: 'hover:border-cyan-300/60 shadow-cyan-500/5',
      rankBg: 'bg-slate-500/20 text-slate-300'
    }
  };

  const styleConfig = colorMap[tier] || colorMap.Match;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      onClick={() => setExpanded(v => !v)}
      className={`relative w-full rounded-2xl border p-5 mb-3 bg-gradient-to-br ${styleConfig.bg} ${styleConfig.hover} shadow-lg cursor-pointer transition-all duration-200`}
      role="button"
      aria-expanded={expanded}
      id={`card-${entry.rank}`}
      style={style}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Left Side Info */}
        <div className="flex items-start gap-4">
          <div className={`w-10 h-10 ${styleConfig.rankBg} font-black text-sm rounded-xl flex items-center justify-center shrink-0`}>
            #{entry.rank}
          </div>
          <div>
            <h4 className="text-sm md:text-base font-bold text-white leading-snug">{entry.college_name}</h4>
            <p className="text-xs font-semibold text-slate-400 mt-1 flex items-center gap-1.5">
              <span>{entry.branch_name}</span>
            </p>
            <div className="flex items-center gap-3 text-[10px] text-slate-500 mt-1">
              <span className="flex items-center gap-1"><MapPin size={10} /> {entry.district}</span>
              <span className="flex items-center gap-1"><Award size={10} /> NIRF Proxy #{entry.nirf_rank_proxy}</span>
            </div>
          </div>
        </div>

        {/* Right Side Status */}
        <div className="flex items-center justify-between sm:justify-end gap-4 sm:text-right shrink-0 border-t border-slate-800/40 pt-3 sm:pt-0 sm:border-0">
          <div className="text-[10px] text-slate-500 sm:text-right">
            <div>{entry.total_seats} Seats Available</div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full ${styleConfig.badge}`}>
              {tier}
            </span>
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
              className="text-slate-400"
            >
              <ChevronDown size={16} />
            </motion.div>
          </div>
        </div>
      </div>

      {/* Expanded explanation */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="mt-4 pt-4 border-t border-white/5 text-xs md:text-sm text-slate-300 leading-relaxed">
              <strong className="block text-white mb-1.5">Placement Strategy:</strong>
              {entry.explanation}
              <div className="flex flex-wrap gap-4 mt-3 text-[10px] text-slate-500">
                <span>Preference Score: {(entry.composite_score * 100).toFixed(1)}%</span>
                <span>Engine Model: {entry.model_used}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

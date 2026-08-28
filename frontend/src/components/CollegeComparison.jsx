// src/components/CollegeComparison.jsx
import { motion } from 'framer-motion';
import {
  X,
  Sparkles,
  Award,
  TrendingUp,
  Building2,
  Star,
  CheckCircle2,
  DollarSign,
  Briefcase,
  MapPin
} from 'lucide-react';

export default function CollegeComparison({ data, onClose }) {
  if (!data) return null;

  const { student_percentile, category_code, comparison_items, ai_decision_summary } = data;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-stone-950/70 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-3xl border border-stone-200 shadow-2xl max-w-6xl w-full p-5 sm:p-8 max-h-[92vh] overflow-y-auto"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-teal-700 text-white flex items-center justify-center shadow-md">
              <TrendingUp size={20} />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-black text-stone-900 flex items-center gap-2">
                Top 5 Colleges Visual Comparison
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
                  {student_percentile}%ile • {category_code}
                </span>
              </h2>
              <p className="text-xs text-stone-500 mt-0.5">
                Placement rates, package metrics, top recruiters & campus galleries for your score
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 text-stone-500 hover:bg-stone-200 flex items-center justify-center transition-colors cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        {/* AI Decision Summary Box */}
        {ai_decision_summary && (
          <div className="my-6 p-5 rounded-2xl bg-gradient-to-r from-teal-900 via-stone-900 to-indigo-950 text-white shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
              <Sparkles size={120} />
            </div>
            
            <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles size={15} className="animate-spin" />
              <span>AI Comparative Insights & Decision Summary</span>
            </div>

            <div className="text-xs sm:text-sm leading-relaxed text-stone-200 whitespace-pre-line">
              {ai_decision_summary}
            </div>
          </div>
        )}

        {/* Comparison Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-6">
          {comparison_items.map((item) => (
            <motion.div
              key={item.college_id}
              whileHover={{ y: -4 }}
              className="rounded-2xl border border-stone-200 bg-stone-50/60 overflow-hidden flex flex-col justify-between shadow-sm hover:shadow-md transition-all"
            >
              {/* Campus Image Header */}
              <div className="relative h-32 w-full overflow-hidden bg-stone-200">
                <img
                  src={item.image_url}
                  alt={item.college_name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-stone-950/80 via-transparent to-transparent" />
                <span className="absolute top-2 left-2 px-2 py-0.5 rounded-md bg-stone-900/80 text-white text-[10px] font-extrabold shadow-sm">
                  #{item.rank} Match
                </span>
                <span className="absolute bottom-2 left-2 text-[11px] font-bold text-white flex items-center gap-1">
                  <MapPin size={11} className="text-teal-400" /> {item.district}
                </span>
              </div>

              {/* College Name & Branch */}
              <div className="p-3 border-b border-stone-200 bg-white">
                <h3 className="text-xs font-extrabold text-stone-900 line-clamp-2 min-h-[32px]">
                  {item.college_name}
                </h3>
                <p className="text-[11px] font-semibold text-teal-700 mt-1 flex items-center gap-1">
                  <Building2 size={11} /> {item.branch_name}
                </p>
                <div className="mt-1 text-[10px] text-stone-500 font-medium">
                  Cutoff: <strong className="text-stone-800">{item.predicted_closing.toFixed(2)} %ile</strong>
                </div>
              </div>

              {/* Placement & Metrics */}
              <div className="p-3 space-y-3 grow bg-white/60">
                
                {/* Placement Rate */}
                <div>
                  <div className="flex justify-between text-[11px] font-bold text-stone-800 mb-1">
                    <span>Placement Rate</span>
                    <span className="text-emerald-700">{item.placement_rate}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-stone-200 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-emerald-600"
                      style={{ width: `${item.placement_rate}%` }}
                    />
                  </div>
                </div>

                {/* Packages */}
                <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                  <div className="p-1.5 rounded-lg bg-teal-50 border border-teal-200">
                    <span className="text-stone-500 block">Avg Package</span>
                    <strong className="text-teal-900 text-xs">{item.avg_package_lpa} LPA</strong>
                  </div>
                  <div className="p-1.5 rounded-lg bg-amber-50 border border-amber-200">
                    <span className="text-stone-500 block">Peak Package</span>
                    <strong className="text-amber-900 text-xs">{item.highest_package_lpa} LPA</strong>
                  </div>
                </div>

                {/* Ratings */}
                <div className="flex items-center justify-between text-[10px] text-stone-600 border-t border-stone-200/60 pt-2">
                  <span className="flex items-center gap-1">
                    <Star size={11} className="text-amber-400 fill-amber-400" /> Lab Rating:
                  </span>
                  <strong className="text-stone-900">{item.lab_quality_rating} / 5</strong>
                </div>

                {/* Top Recruiters */}
                <div>
                  <span className="text-[10px] font-bold text-stone-500 block mb-1">Top Recruiters:</span>
                  <div className="flex flex-wrap gap-1">
                    {item.top_recruiters.slice(0, 4).map((rec, idx) => (
                      <span key={idx} className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-stone-200/80 text-stone-800">
                        {rec}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Highlight Note */}
                <p className="text-[10px] text-stone-500 leading-tight italic pt-1 border-t border-stone-200/60">
                  "{item.highlights}"
                </p>

              </div>

            </motion.div>
          ))}
        </div>

        {/* Modal Footer */}
        <div className="mt-6 pt-4 border-t border-stone-200 flex items-center justify-between text-xs text-stone-500">
          <span>Use placement trends & campus infrastructure to finalize your top preferences.</span>
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-stone-900 text-white font-bold text-xs hover:bg-stone-800 transition-colors shadow-md cursor-pointer"
          >
            Close Dashboard
          </button>
        </div>

      </motion.div>
    </motion.div>
  );
}

// src/components/StudentForm.jsx
import { useEffect, useState } from 'react';
import { getCatalog } from '../api';

const CATEGORIES = [
  { code: 'GOPENH', label: 'Open (Home University)' },
  { code: 'GOBCNH', label: 'OBC-NCL (Home University)' },
  { code: 'GSCNH',  label: 'SC (Home University)' },
  { code: 'GSTNH',  label: 'ST (Home University)' },
  { code: 'GEWSNH', label: 'EWS (Home University)' },
  { code: 'LOPENS', label: 'Open (Other than Home Univ.)' },
];

export default function StudentForm({ onSubmit, loading }) {
  const [percentile, setPercentile] = useState(90.0);
  const [category, setCategory] = useState('GOPENH');
  const [districts, setDistricts] = useState([]);
  const [branches, setBranches] = useState([]);
  const [catalog, setCatalog] = useState({ categories: CATEGORIES, districts: [], branches: [] });

  useEffect(() => {
    getCatalog().then(data => {
      const seen = new Set();
      const uniqueBranches = data.branches.filter(branch => {
        const key = branch.code.trim().toUpperCase();
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      setCatalog({ ...data, branches: uniqueBranches });
    }).catch(() => undefined);
  }, []);

  function toggleDistrict(d) {
    setDistricts(prev =>
      prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d]
    );
  }

  function updateBranches(event) {
    const selectedCodes = Array.from(event.target.selectedOptions, option => option.value);
    setBranches(selectedCodes);
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      percentile: parseFloat(percentile),
      category_code: category,
      preferred_districts: districts,
      preferred_branch_codes: branches,
      max_reach: 100,
      max_match: 100,
      max_safe: 100,
    });
  }

  const sliderPct = ((percentile - 50) / 49.99) * 100;

  return (
    <form onSubmit={handleSubmit} id="student-form" className="w-full">
      <div className="form-panel relative overflow-hidden px-5 py-7 sm:px-8 sm:py-9">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* ── Percentile Slider ── */}
          <div className="col-span-1 md:col-span-2 flex flex-col gap-2">
            <label className="eyebrow" htmlFor="percentile-slider">
              MHT-CET Percentile
            </label>
            <div className="flex items-baseline gap-1">
              <span className="percentile-value">
                {parseFloat(percentile).toFixed(2)}
              </span>
              <span className="text-sm font-semibold text-slate-500">%ile</span>
            </div>
            <input
              id="percentile-slider"
              type="range"
              className="range-slider accent-indigo-500"
              min="50" max="99.99" step="0.01"
              value={percentile}
              style={{
                background: `linear-gradient(to right, #6366f1 0%, #a855f7 ${sliderPct}%, #1e293b ${sliderPct}%)`
              }}
              onChange={e => setPercentile(e.target.value)}
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>50.00</span>
              <span>99.99</span>
            </div>
          </div>

          {/* ── Category ── */}
          <div className="flex flex-col gap-2">
            <label className="eyebrow" htmlFor="category-select">
              Admission Category
            </label>
            <select
              id="category-select"
              className="field-select"
              value={category}
              onChange={e => setCategory(e.target.value)}
            >
              {catalog.categories.map(c => (
                <option key={c.code} value={c.code} className="bg-slate-950">{c.label}</option>
              ))}
            </select>
          </div>

          {/* ── District Preference ── */}
          <div className="flex flex-col gap-2">
            <label className="eyebrow">
              Preferred Districts <span className="text-[10px] text-slate-500 font-normal">(optional)</span>
            </label>
            <div className="choice-grid">
              {catalog.districts.map(d => (
                <button
                  key={d}
                  type="button"
                  id={`district-${d}`}
                    className={`choice-button ${
                    districts.includes(d)
                      ? 'is-selected'
                      : ''
                  }`}
                  onClick={() => toggleDistrict(d)}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* ── Branch Preference ── */}
          <div className="col-span-1 md:col-span-2 flex flex-col gap-2">
            <label className="eyebrow" htmlFor="branch-select">
              Branch Preferences <span className="field-note">(optional, select in priority order)</span>
            </label>
            <select id="branch-select" className="field-select branch-select" multiple value={branches} onChange={updateBranches}>
              {catalog.branches.map(branch => <option key={branch.code} value={branch.code}>{branch.name}</option>)}
            </select>
            {branches.length > 0 && (
              <p className="selection-summary">
                <span>Priority: <span className="font-semibold text-teal-700">{branches.map(code => catalog.branches.find(branch => branch.code === code)?.name).join(' → ')}</span></span>
                <button 
                  type="button" 
                  className="clear-button"
                  onClick={() => setBranches([])}
                >
                  Clear Selection
                </button>
              </p>
            )}
          </div>

        </div>

        {/* ── Submit ── */}
        <div className="mt-8">
          <button
            id="generate-list-btn"
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Predicting cutoffs & ranking…
              </>
            ) : (
              <>✦ Generate My CAP Preference List</>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}

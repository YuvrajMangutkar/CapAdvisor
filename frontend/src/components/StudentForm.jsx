// src/components/StudentForm.jsx
import { useEffect, useState, useRef } from 'react';
import { Search, X, ChevronDown, Check, MapPin, BookOpen } from 'lucide-react';
import { getCatalog } from '../api';

const CATEGORIES = [
  { code: 'GOPENH', label: 'Open (Home University)' },
  { code: 'GOBCNH', label: 'OBC-NCL (Home University)' },
  { code: 'GSCNH',  label: 'SC (Home University)' },
  { code: 'GSTNH',  label: 'ST (Home University)' },
  { code: 'GEWSNH', label: 'EWS (Home University)' },
  { code: 'LOPENS', label: 'Open (Other than Home Univ.)' },
];

const DEFAULT_DISTRICTS = [
  'Pune', 'Mumbai', 'Navi Mumbai', 'Thane', 'Nagpur', 'Nashik',
  'Chhatrapati Sambhajinagar', 'Kolhapur', 'Solapur', 'Sangli', 'Satara',
  'Amravati', 'Latur', 'Nanded', 'Jalgaon', 'Dhule', 'Raigad', 'Ratnagiri'
];

export default function StudentForm({ onSubmit, loading }) {
  const [percentile, setPercentile] = useState(90.0);
  const [category, setCategory] = useState('GOPENH');
  const [districts, setDistricts] = useState([]);
  const [branches, setBranches] = useState([]);
  const [catalog, setCatalog] = useState({ categories: CATEGORIES, districts: DEFAULT_DISTRICTS, branches: [] });

  // Dropdown open & search states
  const [branchOpen, setBranchOpen] = useState(false);
  const [branchSearch, setBranchSearch] = useState('');
  const [cityOpen, setCityOpen] = useState(false);
  const [citySearch, setCitySearch] = useState('');

  const branchRef = useRef(null);
  const cityRef = useRef(null);

  useEffect(() => {
    getCatalog().then(data => {
      const seen = new Set();
      const uniqueBranches = data.branches.filter(branch => {
        const key = branch.code.trim().toUpperCase();
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      const activeDistricts = data.districts && data.districts.length > 0 ? data.districts : DEFAULT_DISTRICTS;
      setCatalog({ ...data, districts: activeDistricts, branches: uniqueBranches });
    }).catch(() => undefined);
  }, []);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (branchRef.current && !branchRef.current.contains(e.target)) {
        setBranchOpen(false);
      }
      if (cityRef.current && !cityRef.current.contains(e.target)) {
        setCityOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function toggleDistrict(d) {
    setDistricts(prev =>
      prev.includes(d) ? prev.filter(x => x !== d) : [...prev, d]
    );
  }

  function toggleBranch(bCode) {
    setBranches(prev =>
      prev.includes(bCode) ? prev.filter(x => x !== bCode) : [...prev, bCode]
    );
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

  // Filtered lists for dropdown search
  const filteredBranches = catalog.branches.filter(b => 
    b.name.toLowerCase().includes(branchSearch.toLowerCase()) || 
    b.code.toLowerCase().includes(branchSearch.toLowerCase())
  );

  const filteredDistricts = catalog.districts.filter(d => 
    d.toLowerCase().includes(citySearch.toLowerCase())
  );

  return (
    <form onSubmit={handleSubmit} id="student-form" className="w-full">
      <div className="form-panel relative overflow-visible px-5 py-6 sm:px-7 sm:py-7">
        <div className="flex flex-col gap-6">

          {/* ── Top Row: Percentile Slider & Category Selection ── */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-end">
            
            {/* Percentile Slider (7 cols) */}
            <div className="md:col-span-7 flex flex-col gap-1.5">
              <label className="eyebrow" htmlFor="percentile-slider">
                MHT-CET Percentile
              </label>
              <div className="flex items-baseline gap-1.5">
                <span className="percentile-value leading-none">
                  {parseFloat(percentile).toFixed(2)}
                </span>
                <span className="text-sm font-bold text-stone-500">%ile</span>
              </div>
              <input
                id="percentile-slider"
                type="range"
                className="range-slider accent-teal-600 mt-1"
                min="50" max="99.99" step="0.01"
                value={percentile}
                style={{
                  background: `linear-gradient(to right, #0f766e 0%, #0f766e ${sliderPct}%, #e2e8f0 ${sliderPct}%)`
                }}
                onChange={e => setPercentile(e.target.value)}
              />
              <div className="flex justify-between text-[10px] font-semibold text-stone-400">
                <span>50.00 %ile</span>
                <span>99.99 %ile</span>
              </div>
            </div>

            {/* Category Select (5 cols) */}
            <div className="md:col-span-5 flex flex-col gap-1.5">
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
                  <option key={c.code} value={c.code}>{c.label}</option>
                ))}
              </select>
            </div>

          </div>

          {/* ── Row 2: Compact Searchable Branch Picker ── */}
          <div className="flex flex-col gap-2 relative" ref={branchRef}>
            <label className="eyebrow flex items-center gap-1.5">
              <BookOpen size={13} className="text-teal-700" /> Branch Preferences
              <span className="field-note">(Optional)</span>
            </label>

            {/* Compact Input Box with Tags inside */}
            <div 
              onClick={() => setBranchOpen(true)}
              className="field-select min-h-[46px] h-auto flex flex-wrap items-center gap-1.5 cursor-pointer bg-white"
            >
              {branches.length === 0 && (
                <span className="text-stone-400 text-xs flex items-center gap-1">
                  <Search size={13} /> Select or search engineering branches...
                </span>
              )}

              {branches.map(code => {
                const bObj = catalog.branches.find(b => b.code === code);
                const label = bObj ? bObj.name : code;
                return (
                  <span 
                    key={code} 
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold shadow-2xs"
                  >
                    {label}
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); toggleBranch(code); }}
                      className="hover:text-teal-950 p-0.5 rounded-full"
                    >
                      <X size={12} />
                    </button>
                  </span>
                );
              })}

              <div className="ml-auto flex items-center gap-1 shrink-0 text-stone-400">
                {branches.length > 0 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setBranches([]); }}
                    className="text-[11px] font-semibold text-stone-400 hover:text-rose-600 mr-1"
                  >
                    Clear
                  </button>
                )}
                <ChevronDown size={16} className={`transition-transform ${branchOpen ? 'rotate-180' : ''}`} />
              </div>
            </div>

            {/* Dropdown Popover */}
            {branchOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 z-30 bg-white border border-stone-200 shadow-xl rounded-2xl p-2 max-h-60 overflow-hidden flex flex-col">
                <div className="p-1 border-b border-stone-100 mb-1 flex items-center gap-2 px-2 bg-stone-50 rounded-xl">
                  <Search size={14} className="text-stone-400" />
                  <input
                    type="text"
                    autoFocus
                    placeholder="Search branches..."
                    value={branchSearch}
                    onChange={(e) => setBranchSearch(e.target.value)}
                    className="w-full text-xs bg-transparent outline-none py-1.5 text-stone-800"
                  />
                  {branchSearch && (
                    <button type="button" onClick={() => setBranchSearch('')} className="text-stone-400 hover:text-stone-600">
                      <X size={12} />
                    </button>
                  )}
                </div>

                <div className="overflow-y-auto space-y-1 grow">
                  {filteredBranches.length === 0 ? (
                    <p className="text-xs text-stone-400 text-center py-3">No matching branches found</p>
                  ) : (
                    filteredBranches.map(b => {
                      const isSel = branches.includes(b.code);
                      return (
                        <button
                          key={b.code}
                          type="button"
                          onClick={() => toggleBranch(b.code)}
                          className={`w-full text-left px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-colors ${
                            isSel ? 'bg-teal-50 text-teal-800 font-bold' : 'hover:bg-stone-100 text-stone-700'
                          }`}
                        >
                          <span>{b.name} <span className="text-[10px] text-stone-400">({b.code})</span></span>
                          {isSel && <Check size={14} className="text-teal-600" />}
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>

          {/* ── Row 3: Compact Searchable City / District Picker ── */}
          <div className="flex flex-col gap-2 relative" ref={cityRef}>
            <label className="eyebrow flex items-center gap-1.5">
              <MapPin size={13} className="text-teal-700" /> Filter by Cities / Districts
              <span className="field-note">(Optional)</span>
            </label>

            {/* Compact Input Box with Tags inside */}
            <div 
              onClick={() => setCityOpen(true)}
              className="field-select min-h-[46px] h-auto flex flex-wrap items-center gap-1.5 cursor-pointer bg-white"
            >
              {districts.length === 0 && (
                <span className="text-stone-400 text-xs flex items-center gap-1">
                  <Search size={13} /> Select or search target cities (e.g. Pune, Mumbai)...
                </span>
              )}

              {districts.map(city => (
                <span 
                  key={city} 
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold shadow-2xs"
                >
                  {city}
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); toggleDistrict(city); }}
                    className="hover:text-teal-950 p-0.5 rounded-full"
                  >
                    <X size={12} />
                  </button>
                </span>
              ))}

              <div className="ml-auto flex items-center gap-1 shrink-0 text-stone-400">
                {districts.length > 0 && (
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setDistricts([]); }}
                    className="text-[11px] font-semibold text-stone-400 hover:text-rose-600 mr-1"
                  >
                    Clear
                  </button>
                )}
                <ChevronDown size={16} className={`transition-transform ${cityOpen ? 'rotate-180' : ''}`} />
              </div>
            </div>

            {/* Dropdown Popover */}
            {cityOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 z-30 bg-white border border-stone-200 shadow-xl rounded-2xl p-2 max-h-60 overflow-hidden flex flex-col">
                <div className="p-1 border-b border-stone-100 mb-1 flex items-center gap-2 px-2 bg-stone-50 rounded-xl">
                  <Search size={14} className="text-stone-400" />
                  <input
                    type="text"
                    autoFocus
                    placeholder="Search cities..."
                    value={citySearch}
                    onChange={(e) => setCitySearch(e.target.value)}
                    className="w-full text-xs bg-transparent outline-none py-1.5 text-stone-800"
                  />
                  {citySearch && (
                    <button type="button" onClick={() => setCitySearch('')} className="text-stone-400 hover:text-stone-600">
                      <X size={12} />
                    </button>
                  )}
                </div>

                <div className="overflow-y-auto space-y-1 grow">
                  {filteredDistricts.length === 0 ? (
                    <p className="text-xs text-stone-400 text-center py-3">No matching cities found</p>
                  ) : (
                    filteredDistricts.map(city => {
                      const isSel = districts.includes(city);
                      return (
                        <button
                          key={city}
                          type="button"
                          onClick={() => toggleDistrict(city)}
                          className={`w-full text-left px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-colors ${
                            isSel ? 'bg-teal-50 text-teal-800 font-bold' : 'hover:bg-stone-100 text-stone-700'
                          }`}
                        >
                          <span>{city}</span>
                          {isSel && <Check size={14} className="text-teal-600" />}
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>

          {/* ── Submit Button ── */}
          <div className="pt-2">
            <button
              id="generate-list-btn"
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating Your Preference List…
                </>
              ) : (
                <>✦ Generate My CAP Preference List</>
              )}
            </button>
          </div>

        </div>
      </div>
    </form>
  );
}

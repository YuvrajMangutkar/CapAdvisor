// src/App.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Compass, Info, ShieldCheck } from 'lucide-react';
import StudentForm from './components/StudentForm';
import ResultsList from './components/ResultsList';
import FloatingBackground from './components/FloatingBackground';
import ContactPage from './components/ContactPage';
import AboutPage from './components/AboutPage';
import { generateList } from './api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [searchParams, setSearchParams] = useState(null);
  const [showContact, setShowContact] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  const handleGenerate = async (params) => {
    setLoading(true);
    setError(null);
    setSearchParams(params);
    try {
      const data = await generateList(params);
      setResults(data);
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }, 300);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="site-shell relative min-h-screen z-10 max-w-6xl mx-auto px-4 pb-20 sm:px-6">
      {/* ── Background Mesh ── */}
      <FloatingBackground />
      {/* ── Navbar ── */}
      <motion.nav 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="site-nav relative z-10 flex items-center justify-between py-5 mb-10"
      >
        <button type="button" className="brand-lockup" onClick={() => { setShowContact(false); setShowAbout(false); }}>
          <div className="brand-mark">
            <Compass size={20} color="white" />
          </div>
          CAP Advisor
        </button>
        <div className="flex items-center gap-4">
          <button type="button" className="nav-action hidden sm:block" onClick={() => { setShowAbout(true); setShowContact(false); }}>About</button>
          <button type="button" className="nav-action hidden sm:block" onClick={() => { setShowContact(true); setShowAbout(false); }}>Contact</button>
          <div className="season-tag">MHT-CET 2026</div>
        </div>
      </motion.nav>

      {showContact ? <ContactPage onBack={() => setShowContact(false)} /> : showAbout ? <AboutPage onBack={() => setShowAbout(false)} /> : <>

      {/* ── Hero ── */}
      <header className="hero-copy text-center py-8 relative z-10">
        <motion.div 
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="kicker inline-flex items-center gap-2 mb-6"
        >
          <Sparkles size={14} className="text-purple-400 animate-pulse" />
          Powered by ML Cutoff Prediction
        </motion.div>
        
        <motion.h1 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight text-stone-950"
        >
          Master your <span className="animated-gradient">CAP Round</span> List.
        </motion.h1>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="text-stone-600 max-w-xl mx-auto text-base md:text-lg leading-relaxed mb-8"
        >
          Don't lose out on a better college because of a badly ordered preference list.
          Enter your details below, and our AI will predict this year's cutoffs and generate
          the mathematically optimal list order.
        </motion.p>
      </header>

      {/* ── Main Form ── */}
      <main className="relative z-10">
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          <StudentForm onSubmit={handleGenerate} loading={loading} />
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
            >
              <strong>Error:</strong> {error}
            </motion.div>
          )}
        </AnimatePresence>

        <ResultsList data={results} searchParams={searchParams} />
      </main>

      <section id="about" className="relative z-10 grid md:grid-cols-2 gap-10 mt-20 pt-10 border-t border-slate-800/80 scroll-mt-8">
        <div className="border-l-2 border-indigo-400/50 pl-5">
          <Info className="text-indigo-300 mb-4" size={22} />
          <h2 className="text-lg font-bold text-white mb-2">Built for real CAP decisions</h2>
          <p className="text-sm leading-6 text-slate-400">CAP Advisor compares historical college and branch cutoffs across every available round, then keeps predictions close to the actual percentile point scale.</p>
        </div>
        <div className="border-l-2 border-emerald-400/50 pl-5">
          <ShieldCheck className="text-emerald-300 mb-4" size={22} />
          <h2 className="text-lg font-bold text-white mb-2">Use the list with confidence</h2>
          <p className="text-sm leading-6 text-slate-400">The spreadsheet contains only the fields needed for a clean preference list. Always cross-check the final choice code and official notice before submission.</p>
        </div>
      </section>

      <section id="contact" className="relative z-10 mt-5 mb-8 p-6 rounded-2xl border border-indigo-400/20 bg-indigo-500/5 scroll-mt-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white">Questions about a CAP cutoff?</h2>
            <p className="text-sm text-slate-400 mt-1">Send the college, branch, category, and round details so the data can be checked precisely.</p>
          </div>
          <button type="button" onClick={() => { setShowContact(true); setShowAbout(false); }} className="inline-flex items-center justify-center gap-2 text-sm font-bold px-4 py-3 rounded-xl bg-indigo-500 text-white hover:bg-indigo-400 transition-colors">Contact support</button>
        </div>
      </section>
      </>}

      {/* ── Footer ── */}
      <footer className="relative z-10 mt-20 pt-8 border-t border-slate-800/60 text-center text-xs text-slate-500 flex flex-col sm:flex-row justify-between items-center gap-4">
        <p>
          &copy; {new Date().getFullYear()} CAP Advisor. All rights reserved.
        </p>
        <div className="flex gap-4">
          <button 
            type="button" 
            className="hover:text-slate-300 transition-colors cursor-pointer" 
            onClick={() => { setShowAbout(true); setShowContact(false); }}
          >
            About
          </button>
          <button 
            type="button" 
            className="hover:text-slate-300 transition-colors cursor-pointer" 
            onClick={() => { setShowContact(true); setShowAbout(false); }}
          >
            Contact Support
          </button>
        </div>
      </footer>
    </div>
  );
}

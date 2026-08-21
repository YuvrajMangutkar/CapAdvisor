import { ArrowLeft, BarChart3, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function AboutPage({ onBack }) {
  return (
    <main className="about-page relative z-10">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeft size={16} /> Back to advisor
      </button>

      <section className="about-hero">
        <span className="kicker">About CAP Advisor</span>
        <h1>Make every preference count.</h1>
        <p>CAP Advisor turns your MHT-CET percentile into a practical, ordered college preference list using historical cutoff patterns and transparent reach, match, and safe recommendations.</p>
      </section>

      <section className="about-grid">
        <article className="about-card">
          <BarChart3 size={22} />
          <h2>Prediction with context</h2>
          <p>We compare historical cutoffs across colleges, branches, categories, and rounds to estimate where your percentile is most competitive.</p>
        </article>
        <article className="about-card">
          <CheckCircle2 size={22} />
          <h2>A list you can use</h2>
          <p>Recommendations are ordered into a clean preference sequence so you can review options quickly before filling the official CAP form.</p>
        </article>
        <article className="about-card">
          <ShieldCheck size={22} />
          <h2>Clear decision support</h2>
          <p>Every result includes its classification, cutoff estimate, available seats, and an explanation of why it appears in your list.</p>
        </article>
      </section>

      <section className="about-process">
        <div>
          <span className="eyebrow">How it works</span>
          <h2>From percentile to preference order.</h2>
        </div>
        <ol>
          <li><strong>01</strong><span>Enter your percentile and admission category.</span></li>
          <li><strong>02</strong><span>Choose optional districts and branches in priority order.</span></li>
          <li><strong>03</strong><span>Review the ranked list and export it for your CAP planning.</span></li>
        </ol>
      </section>
    </main>
  );
}
